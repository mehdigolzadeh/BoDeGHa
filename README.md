# BoDeGa
Bot detector an automated tool to identify bots in GitHub by analysing comments patterns

This tool accepts the name of a GitHub repository and a GitHub API key and computes its output in three steps.
The first step consists of downloading all comments from the specified GitHub repository thanks to GitHub GraphQL API. This step results in a list of commenters and their corresponding comments.
The second step consists of computing the number of comments, empty comments, comment patterns, and inequality between the number of comments within patterns.
The third step simply applies the model we developed on these examples and outputs the prediction made by the model.


## Installation
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

## Usage 
To run the BoDeGa you need to provide GitHub personal access token (API key). You can follow the instruction [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) to obtain a personal access token (You don't need any of permissions in the list).

You can run BoDeGa simply by running `bodega repo_owner\repo_name --apikey <token>`

If you dont pass other parameters, default parameters will be used. Here is the list of parameters:

`--accounts [ACCOUNT [ACCOUNT ...]]` 	**User login of one or more accounts**
> Example: $ bodega repo_owner/repo_name --accounts mehdigolzadeh alexandredecan tommens --key <token>
  
_By default all accounts will be analysed_

`--start-date START_DATE` 		**Starting date of comments to be considered**
> Example: $ bodega repo_owner/repo_name --start-date 01-01-2018 --key <token>
  
_The default start-date is 6 months before the current date. 

`--verbose` **To have verbose output result**
> Example: $ bodega repo_owner/repo_name --verbose --key <token>
 
_The default value is false, if you don't pass this parameter the output will only be the accounts and their type_
  
`--min-comments MIN_COMMENTS` 		**Minimum number of comments to analyze an account**
> Example: $ bodega repo_owner/repo_name --min-comment 20 --key <token>
 
_The default value is 10 comments_

`--max-comments MAX_COMMENTS` 		**Maximum number of comments to be used (default=100)**
> Example: $ bodega repo_owner/repo_name --max-comment 120 --key <token>

_The default value is 100 comments_

`--key APIKEY` 				**GitHub personal access token to download comments from GitHub GraphQL API**
_This parameter is mandatory and you can obtain an access token as as described earlier_

`--text`                	Print results as text.
`--csv`                		Print results as csv.
`--json`                	Print results as json.
> Example: $ bodega repo_owner/repo_name --json --key <token> 

_This group of parameters is the type of output, if you pass JSON you will get the result in JSON format_

## Example of BoDeGa run
```
$ bodega request/request --key <my token> --start-date 01-01-2017  --verbose
                   comments  empty comments  patterns  dispersion prediction                          
account                                                                     
greenkeeperio-bot        12               0         1    0.108246        Bot
stale                   100               0         1    0.000000        Bot
FredKSchott              64               0        53    0.040618      Human
ahmadnassri              11               0        11    0.037776      Human
csvan                    12               0        12    0.031019      Human
dvishniakov              11               0         9    0.068446      Human
hktalent                 11               0        10    0.034367      Human
johnnysprinkles          12               0        11    0.033187      Human
mikeal                  100               0       100    0.035073      Human
nicjansma                12               0        12    0.035834      Human
plroebuck                10               0        10    0.035052      Human
reconbot                 93               0        81    0.036863      Human
simov                    41               0        37    0.031932      Human
```

```
$ bodega fthomas/refined --key <my token> --start-date 01-01-2017  --verbose --min-comments 20 --max-comments 90 --json

[{"comments":90,"empty comments":0,"patterns":2,"dispersion":0.2573516536,"prediction":"Bot"},{"comments":51,"empty comments":0,"patterns":2,"dispersion":0.2291022525,"prediction":"Bot"},{"comments":90,"empty comments":0,"patterns":1,"dispersion":0.1800412851,"prediction":"Bot"},{"comments":36,"empty comments":0,"patterns":36,"dispersion":0.0282932021,"prediction":"Human"},{"comments":20,"empty comments":1,"patterns":20,"dispersion":0.0314103784,"prediction":"Human"},{"comments":90,"empty comments":14,"patterns":63,"dispersion":0.0441294969,"prediction":"Human"},{"comments":43,"empty comments":1,"patterns":43,"dispersion":0.0321397659,"prediction":"Human"}]
```

```
$ bodega servo/servo --key <my token> --verbose --max-comments 80 --csv --accounts bors-servo Darkspirit Eijebong PeterZhizhin SimonSapin highfive

account,comments,empty comments,patterns,dispersion,prediction                                        
bors-servo,80,0,11,0.12661359778212722,Bot
highfive,80,0,6,0.16390462912896814,Bot
Darkspirit,32,0,32,0.025969293313879968,Human
Eijebong,27,2,23,0.02551053114396642,Human
PeterZhizhin,13,0,12,0.025372037602093358,Human
SimonSapin,80,3,57,0.04771309733409579,Human
```
