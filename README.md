# RepoFuse

## Construct CrossCodeEval line completion data retrieved from Repo-specific semantic graph context

1. Follow instructions on [repo_specific_semantic_graph/README.md#install](repo_specific_semantic_graph/README.md#install) to install the Repo-specific semantic graph Python package.
2. Install the rest of the dependencies that the script depend on: `pip install -r retrieval/requirements.txt`
3. Download the CrossCodeEval dataset and the raw data from <https://github.com/amazon-science/cceval>
4. Run `retrieval/construct_cceval_data.py` to construct the Repo-Specific Semantic Graph context data. You can run `python retrieval/construct_cceval_data.py -h` for help on the arguments. For example:

   ```shell
    python retrieval/construct_cceval_data.py -d <path/to/CrossCodeEval>/crosscodeeval_data/python/line_completion_oracle_bm25.jsonl -o <path/to/output_dir>/line_completion_dependency_graph.jsonl -r <path/to/CrossCodeEval>/crosscodeeval_rawdata -j 10 -l python
   ```
