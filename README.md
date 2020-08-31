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
After running las command your command line prompt will change to `(<name>) ...` and now you can install BoDeGa with the pip command.



### Run 
usage: bodega [-h] repository [--accounts [ACCOUNTS [ACCOUNTS ...]]]
              [--start-date START_DATE] [--min-comments MIN_COMMENTS] 
	      [--verbose] [--max-comments MAX_COMMENTS]
              --key APIKEY [--text | --csv | --json]
