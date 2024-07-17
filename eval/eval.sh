model_type=codelm_cfc

# Infile Context的最大长度
inf_seq_length=2048

# 模型名字
model_name=$1
lang=$2

######################Experiment Setting###################
export model_name_or_path={YOUR_MODEL_PATH}
export prompt_file={YOUR_PROMPT_FILE}
export cfc_seq_length_list=0,256,512,1024,2048,4096 # Crossfile content prompt length. Support split by comma
export crossfile_type_list=S_R,Similar,Related # Crossfile Type：Similar、Related、S_R（Both similar and related. Support split by comma
export ranking_strategy_list=UnixCoder,Random # Ranking Strategy: Unixcoder CodeBert Jacarrd Edit BM25 InDegree Es_Orcal
export lang=python # Test Language, Support python java csharp typescript
###########################################################


export ts_lib=./build/$lang-lang-parser.so
export dtype=bf16 # or fp16
export output_dir=./testrun_fim/$lang/${prompt_file_name%.*}
accelerate launch --main_process_port 29502 eval.py \
        --model_type codelm_cfc \
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
        --crossfile_type_list $crossfile_type_list \
        --ranking_strategy_list $ranking_strategy_list \
        --cfc_seq_length_list $cfc_seq_length_list
