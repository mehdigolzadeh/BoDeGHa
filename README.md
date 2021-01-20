# BoDeGHa 
_(previously BoDeGa)_

An automated tool to identify bots in GitHub repositories by analysing pull request and issue comments. This tool is a part of our [study about identifying bots](https://arxiv.org/abs/2010.03303) published in the journal of systems and software journal.
The tool has been developed by Mehdi Golzadeh, researcher at the Software Engineering Lab of the University of Mons (Belgium) as part of his PhD research.

This tool accepts the name of a GitHub repository and requires a GitHub API key to compute its output in three steps.
The first step consists of downloading all pull request and issue comments from the specified repository thanks to GitHub GraphQL API. This step results in a list of commenters and their corresponding pull request and issue comments.
The second step consists of computing the following features that are needed for the classification model: the number of comments, empty comments, comment patterns, and inequality between the number of comments within patterns.
The third step applies the classification model on the repository data and outputs the bot prediction made by the classification model.

Note that the tool comes with a classification model that has been tested using a test set and cannot reach a precision and recall of 100%. The accuracy may differ from one project to another, it really depends on the types of accounts and comments. In some cases such as the use of templates in comments by human commenters may give rise to more misclassifications than usual (details about reasons for misclassifications can again be found in the discussion section of the companion paper). Moreover,  Since we did not investigate the model's performance on less than 10 and more than 100 comments we set the default value of 10 for *--min-comments* and 100 for *--max-comment*, and one can run the tool with other values on their own risk.

**Important note!** When running the tool on a GitHub repository of your choice, it is possible, though unfrequent, for some human accounts or bot accounts to be misclassified by the classification model. If you would encounter such situations while running the tool, please inform us about it, so that we can strive to further improve the accurracy of the classification algorithm.


## Installation
To install BoDeGHa, run the following command:
```
pip install git+https://github.com/mehdigolzadeh/BoDeGHa
```
Given that this tool has many dependencies, and in order not to conflict with already installed packages, it is recommended to use a virtual environment before its installation. You can install and create a _Python virtual environment_ and then install and run the tool in this environment. You can use any virtual environment of your choice. Below are the steps to install and create a virtual environment with **virtualenv**.

Use the following command to install the virtual environment:
```
pip install virtualenv
```
Create a virtual environment in the folder where you want to place your files:
```
virtualenv <name>
```
Start using the environmnet by:
```
source <name>/bin/activate
```
After running this command your command line prompt will change to `(<name>) ...` and now you can install BoDeGHa with the pip command.
When you are finished running the tool, you can quit the environment by:
```
deactivate
```


## Usage 
To run *BoDeGHa* you need to provide a *GitHub personal access token* (API key). You can follow the instruction [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) to obtain such a token (**You don't need any of permissions in the list**).

You can execute the tool with all default parameters by running `bodegha repo_owner\repo_name --key <token>`

Here is the list of parameters:

`--accounts [ACCOUNT [ACCOUNT ...]]` 	**User login of one or more accounts**
> Example: $ bodegha repo_owner/repo_name --accounts mehdigolzadeh alexandredecan tommens --key <token>
  
_By default all accounts in the repository will be analysed_

`--start-date START_DATE` 		**Start date of pull request and issue comments in the repository to be considered**
> Example: $ bodegha repo_owner/repo_name --start-date 01-01-2018 --key <token>
  
_The default start-date is 6 months before the current date. 

`--verbose` **To have verbose output result**
> Example: $ bodegha repo_owner/repo_name --verbose --key <token>

_The default value is false, if you don't pass this parameter the output will only be the accounts and their type_
  
`--min-comments MIN_COMMENTS` 		**Minimum number of pull request and issue comments that are required to analyze an account**
> Example: $ bodegha repo_owner/repo_name --min-comment 20 --key <token>
 
_The default value is 10 comments (the reason explained earlier in this file)_

`--max-comments MAX_COMMENTS` 		**Maximum number of pull request and issue comments to be considered for each account (default=100)**
> Example: $ bodegha repo_owner/repo_name --max-comment 120 --key <token>

_The default value is 100 comments (the reason explained earlier in this file)_

`--key APIKEY` 				**GitHub personal access token required to download comments from GitHub GraphQL API**
_This parameter is mandatory and you can obtain an access token as described earlier_

`--text`                	Output results as plain text
`--csv`                		Output results in comma-separated values (csv) format
`--json`                	Output results in json format
> Example: $ bodegha repo_owner/repo_name --json --key <token> 

_This group of parameters is the type of output, e.g., if you pass --json you will get the result in JSON format_

### As of version 0.2.3
`--exclude [ACCOUNT [ACCOUNT ...]]` **List of accounts to be excluded from the analysis**

> Example: $ bodegha repo_owner/repo_name --exclude mehdigolzadeh alexandredecan tommens --key <token>

### As of version 1.0.0
`--only-predicted` **Only list accounts that the prediction is available**
> Example: $ bodegha repo_owner/repo_name --only-predicted

### As of version 1.0.1
The model trained on the entire ground-truth dataset in order to enhance its prediction power. 

## Examples of BoDeGHa output (for illustration purposes only)
```
$ bodegha request/request --key <my token> --start-date 01-01-2017  --verbose  --only-predicted
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
$ bodegha fthomas/refined --key <my token> --start-date 01-01-2017  --verbose --min-comments 20 --max-comments 90 --json  --only-predicted

[{"account":"codecov","comments":90,"empty comments":0,"patterns":2,"dispersion":0.2501228703,"prediction":"Bot"},{"account":"codecov-io","comments":51,"empty comments":0,"patterns":2,"dispersion":0.2291022525,"prediction":"Bot"},{"account":"scala-steward","comments":90,"empty comments":0,"patterns":1,"dispersion":0.1819953352,"prediction":"Bot"},{"account":"NeQuissimus","comments":36,"empty comments":0,"patterns":36,"dispersion":0.0282932021,"prediction":"Human"},{"account":"erikerlandson","comments":20,"empty comments":1,"patterns":20,"dispersion":0.0314103784,"prediction":"Human"},{"account":"fthomas","comments":90,"empty comments":14,"patterns":63,"dispersion":0.0441094382,"prediction":"Human"},{"account":"howyp","comments":43,"empty comments":1,"patterns":43,"dispersion":0.0321397659,"prediction":"Human"}]
```

```
$ bodegha servo/servo --key <my token> --verbose --max-comments 80 --csv --accounts bors-servo Darkspirit Eijebong PeterZhizhin SimonSapin highfive  --only-predicted

account,comments,empty comments,patterns,dispersion,prediction                                        
bors-servo,80,0,11,0.12661359778212722,Bot
highfive,80,0,6,0.16390462912896814,Bot
Darkspirit,32,0,32,0.025969293313879968,Human
Eijebong,27,2,23,0.02551053114396642,Human
PeterZhizhin,13,0,12,0.025372037602093358,Human
SimonSapin,80,3,57,0.04771309733409579,Human
```

## License
This tool is distributed under [LGPLv3 - GNU Lesser General Public License, version 3.] (https://github.com/mehdigolzadeh/BoDeGHa/blob/master/LICENSE.txt)

