# BoDeGa
Bot detector an automated tool to identify bots in GitHub by analysing comments patterns

This tool accepts the name of a GitHub repository and a GitHub API key and computes its output in three steps.
The first step consists of downloading all comments from the specified GitHub repository thanks to GitHub GraphQL API. This step results in a list of commenters and their corresponding comments.
The second step consists of computing the number of comments, empty comments, comment patterns, and inequality between the number of comments within patterns.
The third step simply applies the model we developed on these examples and outputs the prediction made by the model.


## Usage
To install this tool, you can run the following command:
```
pip install git+https://github.com/mehdigolzadeh/BoDeGa
```
While you can easily install and use this tool by executing the above command, but given that this tool has many dependencies and in order not to conflict with existing packages, it is better to use the following commands before installation. Install and create a Python virtual environment and then use the tool in the virtual environment. 
Here we explain steps to install and create a virtual environment with virtualenv you can use other virtual environment tools as well.

Use the followin command to install:
```
pip install virtualenv
```
Then create one after moving to the folder you want to place the files:
```
virtualenv <name>
```
Start using it by:
```
Source <name>/bin/activate
```
After running this command your command line prompt will change to `(<name>) ...` and now you can install BoDeGa with the pip command.

## Run 
To run the BoDeGa you need to provide GitHub personal access token (API key). You can follow the instruction [here]{https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token} to obtain a personal access token (You don't need any of permissions in the list).

You can run BoDeGa simply by running `bodega repo_owner\repo_name --apikey <token>`

If you dont pass other parameters, default parameters will be used. Here is the list of parameters:

`--accounts [ACCOUNT [ACCOUNT ...]]` 	**User login of one or more accounts. Example: --accounts mehdigolzadeh alexandredecan tommens**

`--start-date START_DATE` 		**Starting date of comments to be considered**
`--verbose` 				**To have verbose output result**
`--min-comments MIN_COMMENTS` 		**Minimum number of comments to analyze an account**
`--max-comments MAX_COMMENTS` 		**Maximum number of comments to be used (default=100)**
`--key APIKEY` 				**GitHub APIv4 key to download comments from GitHub GraphQL API**
`--text`                	Print results as text.
`--csv`                		Print results as csv.
`--json`                	Print results as json.
