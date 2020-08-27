# BoDeGa
Bot detector an automated tool to identify bots in GitHub by analysing comments patterns

This tool accepts the name of a GitHub repository and a GitHub API key and computes its output in three steps.
The first step consists of downloading all comments from the specified GitHub repository thanks to GitHub GraphQL API. This step results in a list of commenters and their corresponding comments.
The second step consists of computing the number of comments, empty comments, comment patterns, and inequality between the number of comments within patterns.
The third step simply applies the model we developed on these examples and outputs the prediction made by the model.

### Run 
usage: bodega [-h] repository [--accounts [ACCOUNTS [ACCOUNTS ...]]]
              [--start-date START_DATE] [--min-comments MIN_COMMENTS] 
	      [--verbose] [--max-comments MAX_COMMENTS]
              --key APIKEY [--text | --csv | --json]
