# RepoFuse

# Data Generation

# Evaluate
After data generation by codegraph, you can start your evaluation by the following step:
1. run `cd eval && pip install -r requirements.txt` to install evaluation environment. 
2. You need to modify the configuration in `eval.sh`, specifically including the following:
+ model_name_or_path:Replace {YOUR_MODEL_PATH} with the path to your model.

+ prompt_file:Replace {YOUR_PROMPT_FILE} with the path to your prompt file.

+ cfc_seq_length_list:Adjust the list of lengths for the crossfile content prompt as needed. You can pass in multiple values at once, separated by commas.

+ crossfile_type:The type of crossfile content you use. You can choose from Similar, Related and S_R. You can pass in multiple values at once, separated by commas.

+ ranking_strategy_list:Specify the ranking strategies to use. You can choose from UnixCoder, Random, CodeBert, Jaccard, Edit, BM25, InDegree, and Es_Orcal.

+ lang:Set the test language. Supported languages are python, java, csharp, and typescript.
