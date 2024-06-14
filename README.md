# RepoFuse

## Construct CKG graph context data from CrossCodeEval dataset

1. Follow instructions on [code_knowledge_graph/README.md#install](code_knowledge_graph/README.md#install) to install the CKG Python package.
2. Install the rest of the dependencies that the script depend on: `pip install -r retrieval/requirements.txt`
3. Download the CrossCodeEval dataset and the raw data from <https://github.com/amazon-science/cceval>
4. Run `retrieval/construct_CrossCodeEval_dependency_graph_context_data.py` to construct the dependency graph context data. You can run `python retrieval/construct_CrossCodeEval_dependency_graph_context_data.py -h` for help on the arguments. For example:

   ```shell
    python retrieval/construct_CrossCodeEval_dependency_graph_context_data.py -d <path/to/CrossCodeEval>/crosscodeeval_data/python/line_completion_oracle_bm25.jsonl -o <path/to/output_dir>/line_completion_dependency_graph.jsonl -r <path/to/CrossCodeEval>/crosscodeeval_rawdata -j 10 -l python
   ```
