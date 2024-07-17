# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import itertools
import logging
import os
import time
import numpy as np
import torch
import random
from accelerate import Accelerator
from accelerate.utils import set_seed
from datasets import load_dataset, Dataset
from torch.utils.data import DataLoader, SequentialSampler
from tqdm import tqdm
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM
)
from copy import deepcopy

import custom_generate
from eval_metric import compute_metric_stmt
from eval_utils import compute_mean_logp
from copy import deepcopy
from functools import partial

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

COMMENT_SYMBOL = {
    "python": "#",
    "java": "//",
    "csharp": "//",
    "typescript": "//"
}

ranking_strategy_to_score_key = {
    "UnixCoder": "unixcoder_score",
    "CodeBert": "codebert_score",
    "Jacarrd": "jacarrd_score",
    "Edit": "edit_score",
    "BM25": "score",
    "InDegree": "score",
    "Es_Orcal": "es_score"
}

def custom_data_collator(features):
    first = features[0]
    batch = {}
    for k, v in first.items():
        if v is not None and not isinstance(v, str):
            if isinstance(v, torch.Tensor):
                batch[k] = torch.stack([f[k] for f in features])
            elif isinstance(v, np.ndarray):
                batch[k] = torch.tensor(np.stack([f[k] for f in features]))
            else:
                batch[k] = torch.tensor([f[k] for f in features])
        if v is not None and isinstance(v, str):
            batch[k] = [f[k] for f in features]

    return batch

def build_datasets(args, tokenizer):
    # Initialize the model and tokenizer
    # when generating, we will use the logits of right-most token to predict the next token
    # so the padding should be on the left
    tokenizer.padding_side = "left"
    tokenizer.pad_token = tokenizer.eos_token if tokenizer.eos_token else tokenizer.bos_token

    raw_datasets = load_dataset("json", data_files=args.prompt_file, cache_dir=args.cache_dir)

    raw_datasets = raw_datasets["train"]
    raw_datasets = raw_datasets.map(lambda example, idx: {'index': idx, **example}, with_indices=True)
    index2taskid = {idx: md["task_id"] for idx, md in zip(raw_datasets["index"], raw_datasets["metadata"])}
    column_names = raw_datasets.column_names

    # Prompt composition
    def prepare_features(examples):
        tokenizer.truncation_side = "left"
        tokenized_inputs = tokenizer(
            examples["prompt"],
            padding="max_length",
            truncation=True,
            max_length=args.max_seq_length - args.gen_length,
            add_special_tokens=False
        )

        features = {k: t for k, t in tokenized_inputs.items()}
        features["index"] = examples["index"]
        return features

    def ranking_crossfile_context(item_list, ranking_strategy):
        if ranking_strategy == "Random":
            random.shuffle(item_list)
        else:
            sort_key = ranking_strategy_to_score_key[ranking_strategy]
            item_list = sorted(item_list, key = lambda x: -x[sort_key])
        
        return item_list


    def prepare_features_cfc(inf_seq_length, crossfile_type, ranking_strategy, examples):
        max_prompt_length = inf_seq_length + args.cfc_seq_length - args.gen_length
        use_key = "list"

        crossfile_context_tokenize_list = []
        if use_key == "text":
            crossfile_context = [ex["text"] for ex in examples["crossfile_context"]]
        else:
            ls_sym = COMMENT_SYMBOL[args.language]
            num_chunk_prompt = []
            num_chunk_similar_prompt = []
            num_chunk_related_prompt = []
            augmented_prompt = 0

            if args.cfc_seq_length == 0:
                crossfile_features = None
                num_chunk_prompt = [0 for _ in range(len(examples["crossfile_context"]))]
                num_chunk_related_prompt = [0 for _ in range(len(examples["crossfile_context"]))]
                num_chunk_similar_prompt = [0 for _ in range(len(examples["crossfile_context"]))]

            else:
                if crossfile_type == "Similar":
                    crossfile_context_list = []
                    for item in examples["crossfile_context"]:
                        item_list = item["list"]
                        for crossfile_context in item_list:
                            crossfile_context["type"] = "similar"

                        item_list = ranking_crossfile_context(item_list, ranking_strategy)
                        crossfile_context_list.append(item_list)
                
                # 使用相关的信息
                elif crossfile_type == "Related":
                    crossfile_context_list = []

                    for item in examples["crossfile_definition_by_dependency_graph"]:
                        item_list = item["list"]
                        for crossfile_context in item_list:
                            crossfile_context["type"] = "related"

                        item_list = ranking_crossfile_context(item_list, ranking_strategy)
                        crossfile_context_list.append(item_list)

                # 使用相似度 + 相关的信息
                elif crossfile_type == "S_R":
                    crossfile_context_list = []
                    
                    #python
                    for x, y in zip(examples["crossfile_context"], examples["crossfile_definition_by_dependency_graph"]):
                        x_list = x["list"]
                        for crossfile_context in x_list:
                            crossfile_context["type"] = "similar"

                        y_list = y["list"]
                        for crossfile_context in y_list:
                            crossfile_context["type"] = "related"

                        item_list = x_list + y_list
                        item_list = ranking_crossfile_context(item_list, ranking_strategy)
                        crossfile_context_list.append(item_list)

                for cfc_chunks in crossfile_context_list:
                    num_chunk_prompt.append(len(cfc_chunks))
                    cfc_text = ""
                    num_chunk_similar = 0
                    num_chunk_related = 0
                    if cfc_chunks:
                        # at least 1 relevant cfc_chunk found
                        init_cfc_text = f"{ls_sym} Here are some relevant code fragments from other files of the repo:\n\n"
                        cfc_length = len(tokenizer.tokenize(init_cfc_text))
                        
                        for cfc_idx, cfc_chunk in enumerate(cfc_chunks):
                            if cfc_chunk[ranking_strategy_to_score_key[ranking_strategy]] > args.min_cfc_score:
                                add_text = f"{ls_sym} the below code fragment is found in {cfc_chunk['filename']}" + "\n"
                                cfc_lines = cfc_chunk["retrieved_chunk"].split('\n')
                                add_text += "\n".join([f"{ls_sym} {cl}" for cl in cfc_lines if cl]) + "\n\n"
                                # check if adding chunk exceeds max length budget for CFC
                                add_text_len = len(tokenizer.tokenize(add_text))
                                if cfc_length + add_text_len <= args.cfc_seq_length:
                                    cfc_text += add_text
                                    cfc_length += add_text_len
                                    # num_chunk_inc += 1
                                    if cfc_chunk["type"] == "similar":
                                        num_chunk_similar += 1
                                    else:
                                        num_chunk_related += 1
                                else:
                                    break
                        if num_chunk_similar + num_chunk_related > 0:
                            cfc_text = init_cfc_text + cfc_text
                            augmented_prompt += 1

                    num_chunk_similar_prompt.append(num_chunk_similar)
                    num_chunk_related_prompt.append(num_chunk_related)
                    crossfile_context_tokenize_list.append(cfc_text)

                tokenizer.truncation_side = "right"
                crossfile_features = tokenizer(
                    crossfile_context_tokenize_list,
                    truncation=True,
                    max_length=args.cfc_seq_length,
                    add_special_tokens=False
                )

        features = {"input_ids": [], "attention_mask": []}
        
        # Support FIM Evaluation
        for idx, (prefix, suffix) in enumerate(zip(examples["prompt"], examples["right_context"])):
            
            allowed_prompt_length = inf_seq_length - args.gen_length

            prefix_length = int(allowed_prompt_length / 2)
            suffix_length = int(allowed_prompt_length / 2)

            tokenizer.truncation_side = "left"
            prefix_feats = tokenizer(
                [prefix],
                truncation=True,
                max_length=prefix_length,
                add_special_tokens=False
            )

            # -4 for Special Tokens in FIM
            tokenizer.truncation_side = "right"
            suffix_feats = tokenizer(
                [suffix],
                truncation=True,
                max_length=suffix_length - 4,
                add_special_tokens=False
            )

            crossfile_tokens = crossfile_features["input_ids"][idx] if crossfile_features is not None else []
            prefix_tokens = prefix_feats["input_ids"][0]
            suffix_tokens = suffix_feats["input_ids"][0]

            if "deepseek" in args.model_name_or_path:
                prompt_feats = {
                    "input_ids": tokenizer.encode("<｜fim▁begin｜>") + crossfile_tokens + prefix_tokens + tokenizer.encode("<｜fim▁hole｜>", add_special_tokens=False) + suffix_tokens + tokenizer.encode("<｜fim▁end｜>", add_special_tokens=False)
                }
            elif "starcoder" in args.model_name_or_path:
                prompt_feats = {
                    "input_ids": tokenizer.encode("<fim_prefix>") + crossfile_tokens + prefix_tokens + tokenizer.encode("<fim_suffix>", add_special_tokens=False) + suffix_tokens + tokenizer.encode("<fim_middle>", add_special_tokens=False)
                }
            elif "qwen" in args.model_name_or_path:
                prompt_feats = {
                    "input_ids": tokenizer.encode("<fim_prefix>") + crossfile_tokens + prefix_tokens + tokenizer.encode("<fim_suffix>", add_special_tokens=False) + suffix_tokens + tokenizer.encode("<fim_middle>", add_special_tokens=False)
                }

            prompt_feats["attention_mask"] = [1 for _ in range(len(prompt_feats["input_ids"]))]

            for k, v in prompt_feats.items():
                if k in features:
                    features[k].append(prompt_feats[k])

        # pad to max_seq_length
        tokenizer.padding_side = "left"
        # features = tokenizer.pad(features, padding="max_length", max_length=args.max_seq_length - args.gen_length)
        features = tokenizer.pad(features, padding="max_length", max_length=max_prompt_length) 
        features["index"] = examples["index"]
        features["num_chunk_prompt"] = num_chunk_prompt
        features["num_chunk_related_prompt"] = num_chunk_related_prompt
        features["num_chunk_similar_prompt"] = num_chunk_similar_prompt
        return features

    if args.model_type in ["codelm", "seq2seqlm"]:
        tokenized_datasets = raw_datasets.map(
            prepare_features,
            batched=True,
            num_proc=args.preprocessing_num_workers,
            remove_columns=column_names,
            load_from_cache_file=not args.overwrite_cache,
            desc="Running tokenizer on dataset",
        )
    elif args.model_type in ["codelm_cfc"]:
        tokenized_datasets = raw_datasets.map(
            partial(prepare_features_cfc, args.inf_seq_length, args.crossfile_type, args.ranking_strategy),
            batched=True,
            num_proc=args.preprocessing_num_workers,
            remove_columns=column_names,
            load_from_cache_file=not args.overwrite_cache,
            desc="Running tokenizer on dataset",
        )
    else:
        raise NotImplementedError("prepare feature functions not implemented for new model type")

    return tokenized_datasets, index2taskid

def model_inference(tokenized_datasets, index2taskid, tokenizer, model = None):
    if args.dtype == 'fp16':
        dtype = torch.float16
    elif args.dtype == 'fp32':
        dtype = torch.float32
    elif args.dtype == 'bf16':
        dtype = torch.bfloat16
    elif args.dtype == 'int8':
        dtype = torch.int8
    else:
        assert False, f'{args.dtype=} not implemented'

    if args.model_type in ["codelm", "codelm_cfc"]:
        if model is None:
            # print("Load Model From {}".format(args.model_name_or_path))
            model = AutoModelForCausalLM.from_pretrained(
                args.model_name_or_path,
                torch_dtype=dtype,
                trust_remote_code=True,
                revision="main",
                use_cache=True
            )
            model = accelerator.prepare_model(model)
        else:
            print("ReUse Previous Model")
    else:
        raise ValueError("Unknown model type")

    total_samples_cnt = len(tokenized_datasets)
    print(f"total samples: {total_samples_cnt}")

    data_sampler = SequentialSampler(tokenized_datasets)
    dataloader = DataLoader(
        tokenized_datasets,
        sampler=data_sampler,
        collate_fn=custom_data_collator,
        batch_size=args.batch_size
    )
    dataloader = accelerator.prepare_data_loader(dataloader)

    tokenizer.pad_token = tokenizer.eos_token if tokenizer.eos_token else tokenizer.bos_token

    # prompt_length = args.max_seq_length - args.gen_length
    prompt_length = args.inf_seq_length + args.cfc_seq_length - args.gen_length
    max_length = args.inf_seq_length + args.cfc_seq_length

    @torch.no_grad()
    def generate_completions(batch):
        output_dict = custom_generate.generate(
            accelerator.unwrap_model(model),
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            max_length=max_length,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            do_sample=args.do_sample,
            num_beams=args.num_beams,
            num_return_sequences=1,
            pad_token_id=tokenizer.pad_token_id,
            return_dict_in_generate=True,
            output_scores=True
        )
        batch_task_id = batch["index"]
        batch_pred = accelerator.pad_across_processes(
            output_dict.sequences, dim=1, pad_index=tokenizer.pad_token_id
        )
        scores = torch.stack(output_dict.scores, dim=1)
        batch_scores = accelerator.pad_across_processes(
            scores, dim=1, pad_index=tokenizer.pad_token_id
        )
        num_chunk_prompt = batch["num_chunk_prompt"]
        num_chunk_related_prompt = batch["num_chunk_related_prompt"]
        num_chunk_similar_prompt = batch["num_chunk_similar_prompt"]

        # batch_scores.shape = (batch_size x num_gpus x num_return_sequences, max_length)
        batch_task_id, batch_pred, batch_scores, num_chunk_prompt, num_chunk_related_prompt, num_chunk_similar_prompt = accelerator.gather((batch_task_id, batch_pred, batch_scores, num_chunk_prompt, num_chunk_related_prompt, num_chunk_similar_prompt))

        batch_pred = batch_pred[:, prompt_length:]
        generated_texts = tokenizer.batch_decode(batch_pred, skip_special_tokens=True)

        mean_logp = compute_mean_logp(batch_scores, batch_pred, tokenizer.pad_token_id)

        
        return batch_task_id.tolist(), generated_texts, mean_logp, num_chunk_prompt.tolist(), num_chunk_related_prompt.tolist(), num_chunk_similar_prompt.tolist()

    all_preds = []
    all_task_ids = []
    all_num_chunk_prompt = []
    all_num_chunk_related_prompt = []
    all_num_chunk_similar_prompt = []
    with torch.no_grad():
        for idx, batch in tqdm(enumerate(dataloader), total=len(dataloader)):
            completions = None
            completion_scores = None
            for seq_idx in range(args.num_return_sequences):
                batch_task_id, generated_texts, mean_logp, num_chunk_prompt, num_chunk_related_prompt, num_chunk_similar_prompt = generate_completions(batch)
                if seq_idx == 0:
                    all_task_ids.extend(batch_task_id)
                    batch_size = len(batch_task_id)
                    completions = [[] for _ in range(batch_size)]
                    completion_scores = [[] for _ in range(batch_size)]

                for j in range(batch_size):
                    completions[j].append(generated_texts[j])
                    completion_scores[j].append(mean_logp[j])

            all_num_chunk_prompt += num_chunk_prompt
            all_num_chunk_related_prompt += num_chunk_related_prompt
            all_num_chunk_similar_prompt += num_chunk_similar_prompt
            if args.num_return_sequences == 1:
                all_preds.extend([c[0] for c in completions])
            else:
                for c, cs in zip(completions, completion_scores):
                    max_score = max(cs)
                    max_index = cs.index(max_score)
                    all_preds.append(c[max_index])

    with open(f"{args.output_dir}/prediction.jsonl", "w", encoding="utf-8") as f_pred:
        id_processed = set()
        for idx, p, num_prompt, num_related_prompt, num_similar_prompt in zip(all_task_ids, all_preds, all_num_chunk_prompt, all_num_chunk_related_prompt, all_num_chunk_similar_prompt):
            if index2taskid[idx] not in id_processed:
                f_pred.write(json.dumps({"task_id": index2taskid[idx], "pred": p, "num_related_prompt": num_related_prompt, "num_similar_prompt":num_similar_prompt, "num_prompt":num_prompt}) + "\n")
                id_processed.add(index2taskid[idx])


    return model

def print_info(args):
    print("########################################Evaluate INFO#######################")
    print("Load Model Path: {}".format(args.model_name_or_path))
    print("CrossFile Seq Length {}".format(args.cfc_seq_length))
    print("CrossFile Type {}".format(args.crossfile_type))
    print("Ranking Strategy {}".format(args.ranking_strategy))
    print("Output Dir {}".format(args.output_dir))
    print("Batch_size {}".format(args.batch_size))
    print("#############################################################################")

    with open(os.path.join(args.output_dir, "evaluate_info.txt"), "w") as f:
        f.write("########################################Evaluate INFO#######################")
        f.write("Load Model Path: {}\n".format(args.model_name_or_path))
        f.write("CrossFile Seq Length {}\n".format(args.cfc_seq_length))
        f.write("CrossFile Type {}\n".format(args.crossfile_type))
        f.write("Ranking Strategy {}\n".format(args.ranking_strategy))
        f.write("Output Dir {}\n".format(args.output_dir))
        f.write("Batch_size {}\n".format(args.batch_size))
        f.write("#############################################################################")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # model inference args
    parser.add_argument("--language", type=str, required=True, help="language name")
    parser.add_argument("--model_name_or_path", default=None, type=str, help="Pre-trained Model Path")
    parser.add_argument(
        "--model_type",
        type=str,
        default="codelm",
        choices=["codelm", "codelm_cfc"],
        help="Model type to be loaded"
    )
    parser.add_argument("--prompt_file_dir", type=str, default=None, help="file with a list of prompts")
    parser.add_argument("--prompt_file", type=str, default=None, help="file with a list of prompts")
    parser.add_argument("--gen_length", type=int, default=50, help="max length of generated token sequence")
    parser.add_argument("--max_seq_length", type=int, default=2048, help="max length of prompt")
    parser.add_argument(
        "--cfc_seq_length",
        type=int,
        default=512,
        help="For model_type=codelm_cfc: Text sequence length corresponding to the retrieved nodes"
    )

    parser.add_argument(
        "--inf_seq_length",
        type=int,
        default=2048,
        help="max seq length for in-file context"
    )

    parser.add_argument(
        "--min_cfc_score",
        type=float,
        default=float('-inf'),
        help="For model_type=codelm_cfc: min score of a chunk to be considered as CFC chunk"
    )
    parser.add_argument("--batch_size", type=int, default=32, help="batch size for code completion")
    parser.add_argument("--stop_token", type=str, default=None, help="Token at which text generation is stopped")
    parser.add_argument("--cache_dir", type=str, default=None)
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="temperature of 1.0 has no effect, lower tend toward greedy sampling"
    )
    parser.add_argument("--output_dir", type=str, default="output_dir", help="output directory to save predictions")
    parser.add_argument("--top_k", type=int, default=0)
    parser.add_argument("--top_p", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=42, help="random seed for initialization")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
    parser.add_argument("--num_return_sequences", type=int, default=1, help="The number of samples to generate.")
    parser.add_argument("--repetition_penalty", type=float, default=1.0, help="The parameter for repetition penalty.")
    parser.add_argument(
        "--preprocessing_num_workers",
        type=int,
        default=1,
        help="The number of processes to use for the preprocessing."
    )
    parser.add_argument(
        "--overwrite_cache",
        type=bool,
        default=False,
        help="Overwrite the cached training and evaluation sets"
    )
    parser.add_argument("--dtype", type=str, default='bf16')
    parser.add_argument("--do_sample", action="store_true", help="whether we do sampling or greedy/beam-search")
    parser.add_argument("--num_beams", type=int, default=1, help="num of beam for beam-search")

    # compute metric args
    parser.add_argument(
        "--ts_lib",
        type=str,
        default="ts_build/build/python-lang-parser.so",
        help="tree-sitter lib for tokenize code"
    )
    # only compute metric
    parser.add_argument("--only_compute_metric", action="store_true", help="only compute metric")

    parser.add_argument("--is_composition", action="store_true", help="is composition")


    # Crossfile-Context Evaluate Config
    # Similar: Only use Similar Context
    # Related: Only use Semantic Context 
    # S_R: Use Both Similar and Semantic Context
    parser.add_argument("--crossfile_type_list", type=str, default="Similar,Related,S_R", help="which crossfile type is used, the value must be in ['Similar', 'Related', 'S_R'], supports multiple input split by comma")

    # Relevance Score Function
    parser.add_argument("--ranking_strategy_list", type=str, default="UnixCoder", help="which relevance score function is used, the value must be in ['UnixCoder', 'Random', 'CodeBert', 'Edit', 'Jacarrd', 'BM25', 'InDegree'], supports multiple input split by comma")
    
    parser.add_argument("--cfc_seq_length_list", type=str, default="4096", help="max seq length of crossfile context, the value must be in [0, 256, 512, 1024, 2048, 4096], supports multiple input split by comma")
    
    args = parser.parse_args()
    set_seed(args.seed, device_specific=False)

    if args.num_return_sequences > 1:
        assert args.do_sample, "sampling must be set to True when num_return_sequences > 1"

    accelerator = Accelerator()

    model_name_or_path = args.model_name_or_path
    model_name = model_name_or_path.split("/")[-1]
    output_dir = os.path.join(args.output_dir, model_name)

    batch_size_dict = {
        0: 8,
        256: 8,
        512: 8,
        1024: 2,
        2048: 2,
        4096: 1
    }

    crossfile_type_list = args.crossfile_type_list.split(",")
    ranking_strategy_list = args.ranking_strategy_list.split(",")
    cfc_seq_length_list = [int(x) for x in args.cfc_seq_length_list.split(",")]

    model = None
    no_cfc_flag = False
    for cfc_seq_length in cfc_seq_length_list:
        for crossfile_type in crossfile_type_list:
            if cfc_seq_length == 0 and no_cfc_flag:
                print("no cfc only compute once, break now...")
                break
            for ranking_strategy in ranking_strategy_list:
                if cfc_seq_length == 0:
                    if no_cfc_flag:
                        print("no cfc only compute once, break now...")
                        break
                    else:
                        print("First Time no Cfc...")
                        no_cfc_flag = True

                if ranking_strategy == "BM25" and crossfile_type != "Similar":
                    continue

                if ranking_strategy == "InDegree" and crossfile_type != "Related":
                    continue 
                    
                args.output_dir = os.path.join(output_dir, "cfc_seq_{}".format(cfc_seq_length), "{}_{}".format(crossfile_type, ranking_strategy))
                args.crossfile_type = crossfile_type
                args.ranking_strategy = ranking_strategy
                args.cfc_seq_length = cfc_seq_length
                args.batch_size = batch_size_dict[cfc_seq_length]

                if os.path.exists(os.path.join(args.output_dir, "results.json")):
                    print("Skip {}".format(args.output_dir))
                    continue

                if accelerator.is_main_process and not os.path.isdir(args.output_dir):
                    os.makedirs(args.output_dir)
                    print_info(args)
                
                if not args.only_compute_metric:
                    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path, trust_remote_code=True)
                    tokenized_datasets, index2taskid = build_datasets(args, tokenizer)
                    model = model_inference(tokenized_datasets, index2taskid, tokenizer, model)

                # check if the process is the main process
                if accelerator.is_main_process:
                    time.sleep(1)
                    args_copy = deepcopy(args)
                    compute_metric_stmt(args_copy)
                else:
                    print("I'm waiting for the main process to finish its sleep...")

                accelerator.wait_for_everyone()
                print("EveryOne is Here")