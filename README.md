# RepoFuse

# Data Generation


# RepoFuse

## Construct CrossCodeEval line completion data retrieved from Repo-specific semantic graph context

1. Follow instructions on [repo_specific_semantic_graph/README.md#install](repo_specific_semantic_graph/README.md#install) to install the Repo-specific semantic graph Python package.
2. Install the rest of the dependencies that the script depend on: `pip install -r retrieval/requirements.txt`
3. Download the CrossCodeEval dataset and the raw data from <https://github.com/amazon-science/cceval>
4. Run `retrieval/construct_cceval_data.py` to construct the Repo-Specific Semantic Graph context data. You can run `python retrieval/construct_cceval_data.py -h` for help on the arguments. For example:

   ```shell
    python retrieval/construct_cceval_data.py -d <path/to/CrossCodeEval>/crosscodeeval_data/python/line_completion_oracle_bm25.jsonl -o <path/to/output_dir>/line_completion_dependency_graph.jsonl -r <path/to/CrossCodeEval>/crosscodeeval_rawdata -j 10 -l python
   ```

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
3. Run `bash eval.sh`