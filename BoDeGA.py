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

# --- Global vars ---
__API_KEY = "2224398867be11f4221a33549e4c16857bb3b4f3"
__Issues_pulls = 20
__Comments = 20
__User = ''
__Repository = ''

# --- Prerequisites ---
import numpy as np
import pickle
import threading
from Levenshtein import distance as lev
import itertools
from sklearn.cluster import DBSCAN
import json
import os
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
import argparse
from tqdm import tqdm

# --- Exception ---
class BotDetectorError(ValueError):
    pass

# --- Download comments ---
def get_comment_search_query():
    query = """
    query{
    search(first: %d, type: ISSUE, query: "repo:%s involves:%s") {
        edges {
        node {
            ... on PullRequest {
            author{
                login
            }
            body
            comments(first:%d)
            {
                edges{
                node{
                    author{
                    login
                    }
                    body
                }
                }
            }
            }
        }
        node {
            ... on Issue {
            author{
                login
            }
            body
            comments(first:%d)
            {
                edges{
                node{
                    author{
                    login
                    }
                    body
                }
                }
            }
            }
        }
        }
    }
    }"""%(__Issues_pulls,__Repository,__User, __Comments,__Comments)
    return query

def process_comments(response):
    comments = []
    json_object = json.loads(response)
    if 'data' in json_object:
        for edge in json_object["data"]["search"]["edges"]:
            if edge['node']['author']['login'] == __User :
                comments.append(edge['node']['body'])
            if 'comments' in edge['node'] :    
                for comment in edge['node']['comments']['edges'] :
                    if comment['node']['author'] is not None :
                        if comment['node']['author']['login'] == __User :
                            comments.append(comment['node']['body'])
    return comments

def download_comments():
    req = Request("https://api.github.com/graphql", json.dumps({"query": get_comment_search_query()}).encode('utf-8'))
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer {}".format(__API_KEY))
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

def predict(model,sample):
    return 'Bot' if model.predict(sample)[0] == 1 else 'Human'

# --- Thread and progress ---
def run_function_in_thread(pbar, function,max_value, args=[], kwargs={}):
    ret = [None]
    def myrunner(function, ret, *args, **kwargs):
        ret[0] = function(*args, **kwargs)

    thread = threading.Thread(target=myrunner, args=(function, ret) + tuple(args), kwargs=kwargs)
    thread.start()
    while thread.is_alive():
        thread.join(timeout=.2)
        if(pbar.n<max_value):
            pbar.update(.2)
    pbar.n = max_value
    return ret[0]

def progress():
    pbar = tqdm(total=10,smoothing=1,bar_format='{desc}: {percentage:3.0f}%|{bar}')
    tasks =['Downloading messages','Analyzing comments','Computing clusters','Generate features','Loading model','Prediction','Exporting result']
    pbar.set_description(tasks[0])
    response = run_function_in_thread(pbar,download_comments,1.5)

    pbar.set_description(tasks[1])
    comments = run_function_in_thread(pbar,process_comments,4.5,args=(response,))[:100]

    if(len(comments)<10):
        pbar.close()
        raise BotDetectorError('Available comments are not enough for clustering. For clustering we need at least 10 comments')

    pbar.set_description(tasks[2])
    clusters, gini_clusters = run_function_in_thread(pbar,compute_clusters,7.5,args=(comments,))

    pbar.set_description(tasks[3])
    empty_comments = count_empty_comments(comments)
    comments_count = len(comments)
    pbar.n = 7.5

    pbar.set_description(tasks[4])
    model = run_function_in_thread(pbar,load_model,8.5)

    pbar.set_description(tasks[5])
    sample = np.array((comments_count,empty_comments,clusters,gini_clusters[0]),dtype=object).reshape(1,-1)
    result = run_function_in_thread(pbar,predict,9,args=(model,sample))
    
    pbar.n =10
    pbar.set_description(tasks[6])
    pbar.close()
    print('Comments: ',comments_count)
    print('Empty comments: ',empty_comments)
    print('Number of clusters: ',clusters)
    print('Comments dispersion: ', gini_clusters[0])
    print('------------------------------------------')
    print('Prediction: ',result)

# --- cli ---
def arg_parser():
    parser = argparse.ArgumentParser(description='BoDeGa - Bot detection in Github')
    parser.add_argument('user', type=str, help='Paths to one or more git repositories')
    parser.add_argument('-r','--repository', type=str, help='User login you want to check')
    parser.add_argument('-p','--pullissue', type=int, required=False, default=20, help='Number of pull requests and issues to download')
    parser.add_argument('-c','--comments', type=int, required=False, default=20, help='Number of comments of each pull request and issue to download')
    parser.add_argument('-k','--apikey', metavar='APIKEY', type=str, default=__API_KEY, help='API key to download comments from api v4')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--text', action='store_true', help='Print results as text.')
    group.add_argument('--csv', action='store_true', help='Print results as csv.')
    group.add_argument('--json', action='store_true', help='Print results as json.')
    group.add_argument('--plot', nargs='?', const=True, help='Export results to a plot. Filepath can be optionaly specified.')

    return parser.parse_args()

def cli():
    global __User, __Repository,__Issues_pulls,__Comments,__API_KEY
    cliargs = arg_parser()

    __User = cliargs.user

    if cliargs.repository == '.':
        raise BotDetectorError('A repository name is required to download comments. format(repository_owner/repository_name)')
    else:
        __Repository = cliargs.repository

    if cliargs.pullissue > 100 :
        raise BotDetectorError('Cannot download more than 100 Pull and Issues in 1 request.')
    elif cliargs.pullissue < 1 :
        raise BotDetectorError('You should download at least 1 issue and pull request.')
    else:
        __Issues_pulls = cliargs.pullissue
    
    if cliargs.comments > 100 :
        raise BotDetectorError('Cannot download more than 100 Comments in 1 request.')
    elif cliargs.comments < 5 :
        raise BotDetectorError('You should download at least 5 comments.')
    else:
        __Comments = cliargs.comments
    
    if cliargs.apikey == '.':
        raise BotDetectorError('An api key is required to start the process. Please read the documentation to know more about api key')
    else:
        __API_KEY = cliargs.apikey

    # res = len()
    progress()

if __name__ == '__main__':
    cli()