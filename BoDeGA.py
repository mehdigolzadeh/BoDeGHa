##  Module botdetector.py
##
##  Copyright (c) 2020 Mehdi Golzadeh <golzadeh.mehdi@gmail.com>.
##
##  Licensed under GNU Lesser General Public License version 3.0 (LGPL3);
##  you may not use this file except in compliance with the License.
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.


"""
Descriptions

"""


# --- Prerequisites ---
from multiprocessing import Pool
import pandas
import numpy as np
import pickle
import threading
from Levenshtein import distance as lev
import itertools
from sklearn.cluster import DBSCAN
import json
import os
import dateutil
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
import argparse
from tqdm import tqdm

# --- Global vars ---
__Repository = ''
__Users = []
__Date =  None
__Verbose = False
__Comments = 10
__MaxComments = 100
__APIKEY = "2224398867be11f4221a33549e4c16857bb3b4f3"

__Issues = True
__Pulls = True

__Printdata = 'csv'

# --- Exception ---
class BotDetectorError(ValueError):
    pass

# --- Download comments ---
def get_comment_search_query(pr, issue, beforePr, beforeIssue):
    
    owner = __Repository.split('/')[0]
    name = __Repository.split('/')[1]

    pulls = """
        pullRequests(last:100 %s orderBy: {field: CREATED_AT, direction: ASC})
        {
        totalCount
        pageInfo{
                startCursor
                endCursor
        }
        edges{
            cursor
            node{
            author{
                login
            }
            body
            number
            createdAt
            comments(first:100)
            {
                totalCount
                pageInfo{
                    startCursor
                    endCursor
                }
                edges{
                cursor
                node{
                    author{
                    login
                    }
                    body
                    createdAt
                }
                }
            }
            }
        }
        }
    """%('before:"'+beforePr+'"' if beforePr != None else '')

    issues = """
        issues(last:100 %s orderBy: {field: CREATED_AT, direction: ASC})
        {
        totalCount
        pageInfo{
                startCursor
                endCursor
        }
        edges{
            cursor
            node{
            author{
                login
            }
            body
            number
            createdAt
            comments(first:100)
            {
                pageInfo{
                    startCursor
                    endCursor
                }
                edges{
                cursor
                node{
                    author{
                    login
                    }
                    body
                    createdAt
                }
                }
            }
            }
        }
        }
    """%('before:"'+beforeIssue+'"' if beforeIssue != None else '')

    query = """
    {
    repository(owner:"%s", name:"%s"){
        createdAt
        %s
        %s
    }
    }
    """%(owner,name,(pulls if __Pulls and pr else ''), (issues if __Issues and issue else ''))
    return query

def extract_data(data,issue_type='issues'):
    df = pandas.DataFrame()
    json_object = json.loads(data)
    if 'data' not in json_object:
        return
    data = json_object["data"]["repository"]
    issue_total = data[issue_type]['totalCount']
    start_cursor = data[issue_type]['pageInfo']['startCursor']
    end_cursor = data[issue_type]['pageInfo']['endCursor']
    issue_count = len(data[issue_type]['edges'])
    last_date = None
    for issue in data[issue_type]['edges']:
        issue = issue['node']
        date = dateutil.parser.parse(issue['createdAt'],ignoretz=True)
        if date == None:
            continue
        if date > __Date:
            df = df.append({
                'author': (issue['author']['login'] if (issue['author'] !=None) else  np.nan),
                'body':(issue['body'] if issue['body']!=None else ""),
                'number':issue['number'],
                'created_at': date,
                'type':issue_type,
                'empty':(1 if len(issue['body'])<2 else 0)
            },ignore_index=True)
            for comment in issue['comments']['edges']:
                comment = comment['node']
                df = df.append({
                    'author': (comment['author']['login'] if (comment['author'] != None) else  np.nan),
                    'body':comment['body'],
                    'number':issue['number'],
                    'created_at': dateutil.parser.parse(comment['createdAt'],ignoretz=True),
                    'type':issue_type+"_comment",
                    'empty':(1 if len(comment['body'])<2 else 0)
                },ignore_index=True)
        else:
            last_date = date
    return df,issue_total,issue_count,start_cursor,last_date

def process_comments():
    comments = pandas.DataFrame()
    pr=True
    issue=True
    beforePr=None
    beforeIssue=None
    while True:
        data = download_comments(pr, issue, beforePr, beforeIssue);
        
        if pr:
            df_pr,pr_total,pr_count,pr_end_cursor,last_pr = extract_data(data,'pullRequests');
            comments = comments.append(df_pr,ignore_index=True)
        if issue:
            df_issues,issue_total,issue_count ,issue_end_cursor,last_issue = extract_data(data,'issues');
            comments = comments.append(df_issues,ignore_index=True)

        downloaded_issues = len(comments[lambda x: x['type'] == 'issues'].drop_duplicates('number'))
        downloaded_prs = len(comments[lambda x: x['type'] == 'pullRequests'].drop_duplicates('number'))
          
        if last_issue == None and issue_total > downloaded_issues:
            issue = True
            beforeIssue = issue_end_cursor
        else:
            issue = False
        if last_pr == None and pr_total > downloaded_prs:
            pr = True
            beforePr = pr_end_cursor
        else:
            pr = False
            
        if not issue and not pr:
            break
    return comments

def download_comments(pr=True, issue=True, beforePr=None, beforeIssue=None):
    req = Request("https://api.github.com/graphql", json.dumps({"query": get_comment_search_query(pr, issue, beforePr, beforeIssue)}).encode('utf-8'))
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer {}".format(__APIKEY))
    response = urlopen(req)
    return response.read()

# --- Text process and feature production ---
def tokenizer(text):
    return text.split(' ')

def compute_distance(items, distance):
    """ 
    Computes a distance matrix for given items, using given distance function.
    """
    m = np.zeros((len(items), len(items)))
    enumitems = list(enumerate(items))
    for xe, ye in itertools.combinations(enumitems, 2):
        i, x = xe
        j, y = ye
        d = distance(x, y)
        m[i,j] = m[j,i] = d
    return m

def jaccard(x, y):
    """
    To tokenize text and compute jaccard disatnce
    """
    x_w = set(tokenizer(x))
    y_w = set(tokenizer(y))
    return len(x_w.symmetric_difference(y_w)) / (len(x_w.union(y_w)) if len(x_w.union(y_w))>0 else 1)

def levenshtein(x, y, n=None):
    if n is not None:
        x = x[:n]
        y = y[:n]
    return lev(x, y) / (max(len(x), len(y)) if max(len(x), len(y)) >0 else 1)

def average_jac_lev(x, y):
    """
    Computes average of jacard and levenshtein for 2 given strings
    """
    return (jaccard(x, y) + levenshtein(x, y)) / 2

def gini(x):
    """
    Computes Gini inequality metric for a given array
    """
    mad = np.abs(np.subtract.outer(x, x)).mean()
    rmad = mad/np.mean(x)
    g = 0.5 * rmad
    return g

def compute_clusters(itemsarr):
    clustering = DBSCAN( 0.5, min_samples=1, metric='precomputed')
    items = compute_distance(itemsarr, average_jac_lev)
    clusters = clustering.fit_predict(items)
    gini_ = gini(np.tril(items)),
    return (len(set(clusters))) ,gini_

def count_empty_comments(comments):
    empty_comments = 0
    for comment in comments:
        if comment == "":
            empty_comments += 1
    return empty_comments

# --- Load model and prediction ---
def load_model():
    filename = "model.pkl"
    with open(filename, 'rb') as file:
        model = pickle.load(file)
    return model

def predict(model,df):
    df = (
        df
        .assign(
            account_type =lambda x: np.where(model.predict(x[['comments','empty_comments','clusters','gini']]) == 1,'Bot', 'Human')
        )
    )
    return df

# --- Thread and progress ---

def task(data):
    author, group, params = data
    group = group[:__MaxComments]
    clustering = DBSCAN(eps=params['eps'], min_samples=1, metric='precomputed')
    items = compute_distance(getattr(group, params['source']), params['func'])
    clusters = clustering.fit_predict(items)
    empty_comments = np.count_nonzero(group['empty'])
    
    return (
        author,
        len(group),
        empty_comments,
        len(np.unique(clusters)),
        gini(items[pandas.np.tril(items).astype(bool)]),
    )

def run_function_in_thread(pbar, function,max_value, args=[], kwargs={}):
    ret = [None]
    def myrunner(function, ret, *args, **kwargs):
        ret[0] = function(*args, **kwargs)

    thread = threading.Thread(target=myrunner, args=(function, ret) + tuple(args), kwargs=kwargs)
    thread.start()
    while thread.is_alive():
        thread.join(timeout=.1)
        if(pbar.n<max_value):
            pbar.update(.1)
    pbar.n = max_value
    return ret[0]

def progress():
    download_progress = tqdm(total=25,desc='Downloading comments',smoothing=.1,bar_format='{desc}: {percentage:3.0f}%|{bar}')
    comments = run_function_in_thread(download_progress,process_comments,25)
    download_progress.close()

    df = (
        comments
        [comments['author'].isin(
            comments
            .groupby('author',as_index=False)
            .count()[lambda x: x['body']>=10]['author'].values
        )]
        .sort_values('created_at',ascending=False)
    )

    if(len(df)<1):
        raise BotDetectorError('Available comments are not enough to predict type of accounts')

    inputs = []
    for author, group in df.groupby('author'):
        inputs.append((author, group.copy(), {'func': average_jac_lev, 'source': 'body', 'eps': 0.5}))
            
    data = []
    with Pool() as pool:
        for result in tqdm(pool.imap_unordered(task, inputs),desc='Computing features',total=len(inputs),smoothing=.1,bar_format='{desc}: {percentage:3.0f}%|{bar}'):
            data.append(result)
            
    df_clusters = pandas.DataFrame(data=data, columns=['account', 'comments','empty_comments', 'clusters', 'gini'])
    
    prediction_progress = tqdm(total=25,smoothing=.1,bar_format='{desc}: {percentage:3.0f}%|{bar}')
    tasks =['Loading model','Making prediction','Exporting result']
    prediction_progress.set_description(tasks[0])
    model = run_function_in_thread(prediction_progress,load_model,5)

    prediction_progress.set_description(tasks[1])
    result = run_function_in_thread(prediction_progress,predict,25,args=(model,df_clusters))
    prediction_progress.close()

    if __Printdata == 'json':
        print(result.to_json(orient='records'))
    elif __Printdata == 'csv':
        print(result.to_csv())
    else:
        print(result)

# --- cli ---
def arg_parser():
    parser = argparse.ArgumentParser(description='BoDeGa - Bot detection in Github')
    parser.add_argument('repository', help='Paths to a git repositories.')
    parser.add_argument('-u','--users', required=False, default=list(), type=str , nargs='*', help='User login of one or more accounts. Example: -u mehdigolzadeh alexandredecan tommens')
    parser.add_argument('-d','--date', type=lambda d: dateutil.parser.parse(d), required=False, default=None, help='Date regarding the recency of comments (default to None)')
    parser.add_argument('-v','--verbose', action='store_true', required=False, default=False, help='To have verbose')
    parser.add_argument('-c','--comments', type=int, required=False, default=10, help='Minimum number of comments to analyze an account')
    parser.add_argument('-m','--maximum-comments', type=int, required=False, default=100, help='Maximum number of comments to be used (default=100)')
    parser.add_argument('-k','--apikey', metavar='APIKEY', type=str, default=__APIKEY, help='API key to download comments from api v4')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('--only-pulls', action='store_true', help='Only download pull comments.')
    group1.add_argument('--only-issues', action='store_true', help='Only download issue comments.')

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('--text', action='store_true', help='Print results as text.')
    group2.add_argument('--csv', action='store_true', help='Print results as csv.')
    group2.add_argument('--json', action='store_true', help='Print results as json.')

    return parser.parse_args()

def cli():
    global __Repository, __Users, __Date, __Verbose, __Comments,__MaxComments, __APIKEY, __Issues, __Pulls, __Printdata

    args = arg_parser()

    __Repository = args.repository

    __Users = args.users

    __Date = args.date
    __Verbose = args.verbose

    __Issues = not args.only_pulls
    __Pulls = not args.only_issues
    
    if args.comments < 10 :
        raise BotDetectorError('Minimum number of required comments for the model is 10.')
    else:
        __Comments = args.comments

    if args.maximum_comments < 10 :
        raise BotDetectorError('Maximum number of comments cannot be less than 10.')
    else:
        __MaxComments = args.maximum_comments
    
    if args.apikey == '.':
        raise BotDetectorError('An api key is required to start the process. Please read the documentation to know more about api key')
    else:
        __APIKEY = args.apikey

    if args.csv :
        __Printdata = 'csv'
    elif args.json :
        __Printdata = 'json'
    else:
        __Printdata = 'text'
    progress()

if __name__ == '__main__':
    cli()