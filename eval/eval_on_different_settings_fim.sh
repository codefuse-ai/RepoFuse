model_type=codelm_cfc

# Infile Context的最大长度
inf_seq_length=2048

# 模型名字
model_name=$1
lang=$2

if [ "$lang" = "python" ]; then
    prompt=line_completion_rg1_bm25.jsonl
elif [ "$lang" = "java" ]; then
    prompt=aicc_bm25_import
elif [ "$lang" = "csharp" ]; then
    prompt=line_completion_dependency_graph_c_sharp_v1
elif [ "$lang" = "typescript" ]; then
    prompt=line_completion_dependency_graph_typescript_v2
fi

export model_type=$model_type # or codelm for no cross-file context eval

export model_name_or_path=/mnt/user/hongchen/208364/projects/nonsense_experiments/models/$model_name
export lang=$lang
export ts_lib=./build/$lang-lang-parser.so
export dtype=bf16 # or fp16
export prompt_file=/mnt/user/hongchen/329710/resources/cceval/data/crosscodeeval_data/$lang/$prompt.jsonl # or other options in the dir, which corresponds to different retrieval methods and/or retrieval settings
export max_seq_length=$max_seq_length
export cfc_seq_length=$cfc_seq_length 
export output_dir=./testrun_fim/$model_type/$lang/${prompt}

accelerate launch --main_process_port 29502 eval_on_different_settings_fim.py \
        --model_type $model_type \
        --model_name_or_path $model_name_or_path \
        --prompt_file $prompt_file \
        --gen_length 50 \
        --output_dir $output_dir \
        --dtype $dtype \
        --num_return_sequences 1 \
        --overwrite_cache True \
        --ts_lib $ts_lib \
        --language $lang \
        --inf_seq_length $inf_seq_length \
        --crossfile_type_list Similar \
        --ranking_strategy_list UnixCoder \
        --cfc_seq_length_list 0
