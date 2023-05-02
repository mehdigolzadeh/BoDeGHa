#  Module bodegha.py
#
#  Copyright (c) 2020 Mehdi Golzadeh <golzadeh.mehdi@gmail.com>
#
#  Licensed under GNU Lesser General Public License version 3.0 (LGPL3);
#  you may not use this file except in compliance with the License.
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


"""
Descriptions
"""


# --- Prerequisites ---
from multiprocessing import Pool
import pandas
import pickle
import threading
from Levenshtein import distance as lev
import itertools
from sklearn.cluster import DBSCAN
import json
import sys
import dateutil
import pkg_resources
import numpy as np
from dateutil.relativedelta import relativedelta
from datetime import datetime
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
import argparse
from tqdm import tqdm


# --- Exception ---
class BodeghaError(ValueError):
    pass


# --- Download comments ---
def get_comment_search_query(repository, pr, issue, beforePr, beforeIssue):

    owner, name = repository.split('/')

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
    """ % ('before:"'+beforePr+'"' if beforePr is not None else '')

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
    """ % ('before:"'+beforeIssue+'"' if beforeIssue is not None else '')

    query = """
    {
    repository(owner:"%s", name:"%s"){
        createdAt
        %s
        %s
    }
    }
    """ % (owner, name, (pulls if pr else ''), (issues if issue else ''))
    return query


def extract_data(data, date_limit, issue_type='issues'):
    df = pandas.DataFrame()
    json_object = json.loads(data.decode('utf-8'))
    if 'data' not in json_object:
        return
    data = json_object["data"]["repository"]
    if data == None:
        raise BodeghaError(json_object["errors"][0]["message"])
    issue_total = data[issue_type]['totalCount']
    start_cursor = data[issue_type]['pageInfo']['startCursor']
    issue_count = len(data[issue_type]['edges'])
    last_date = None
    for issue in data[issue_type]['edges']:
        issue = issue['node']
        date = dateutil.parser.parse(issue['createdAt'], ignoretz=True)
        if date is None:
            continue
        if date > date_limit:
            df = df.append({
                'author': (issue['author']['login'] if (issue['author'] is not None) else np.nan),
                'body': (issue['body'] if issue['body'] is not None else ""),
                'number': issue['number'],
                'created_at': date,
                'type': issue_type,
                'empty': (1 if len(issue['body']) < 2 else 0)
            }, ignore_index=True)
            for comment in issue['comments']['edges']:
                comment = comment['node']
                df = df.append({
                    'author': (
                        comment['author']['login'] if (comment['author'] is not None) else np.nan
                        ),
                    'body': comment['body'],
                    'number': issue['number'],
                    'created_at': dateutil.parser.parse(comment['createdAt'], ignoretz=True),
                    'type': issue_type + "_comment",
                    'empty': (1 if len(comment['body']) < 2 else 0)
                }, ignore_index=True)
        else:
            last_date = date
    return df, issue_total, issue_count, start_cursor, last_date


def process_comments(repository, accounts, date, min_comments, max_comments, apikey):
    comments = pandas.DataFrame()
    pr = True
    issue = True
    beforePr = None
    beforeIssue = None
    while True:
        data = download_comments(repository, apikey, pr, issue, beforePr, beforeIssue)

        if pr:
            df_pr, pr_total, pr_count, pr_end_cursor, last_pr \
                = extract_data(data, date, 'pullRequests')
            comments = comments.append(df_pr, ignore_index=True)
        if issue:
            df_issues, issue_total, issue_count, issue_end_cursor, last_issue = \
                extract_data(data, date, 'issues')
            comments = comments.append(df_issues, ignore_index=True)

        if len(comments)>0:
            downloaded_issues = \
                len(comments[lambda x: x['type'] == 'issues'].drop_duplicates('number'))
            downloaded_prs = \
                len(comments[lambda x: x['type'] == 'pullRequests'].drop_duplicates('number'))

        if issue and last_issue is None and issue_total > downloaded_issues:
            issue = True
            beforeIssue = issue_end_cursor
        else:
            issue = False
        if pr and last_pr is None and pr_total > downloaded_prs:
            pr = True
            beforePr = pr_end_cursor
        else:
            pr = False

        if not issue and not pr:
            break

    return comments


def download_comments(repository, apikey, pr=True, issue=True, beforePr=None, beforeIssue=None):
    req = Request(
            "https://api.github.com/graphql",
            json.dumps(
                {
                    "query": get_comment_search_query(repository, pr, issue, beforePr, beforeIssue)
                }
            ).encode('utf-8')
        )
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer {}".format(apikey))
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
        m[i, j] = m[j, i] = d
    return m


def jaccard(x, y):
    """
    To tokenize text and compute jaccard disatnce
    """
    x_w = set(tokenizer(x))
    y_w = set(tokenizer(y))
    return (
        len(x_w.symmetric_difference(y_w)) / (len(x_w.union(y_w)) if len(x_w.union(y_w)) > 0 else 1)
    )


def levenshtein(x, y, n=None):
    if n is not None:
        x = x[:n]
        y = y[:n]
    return lev(x, y) / (max(len(x), len(y)) if max(len(x), len(y)) > 0 else 1)


def average_jac_lev(x, y):
    """
    Computes average of jacard and levenshtein for 2 given strings
    """
    return (jaccard(x, y) + levenshtein(x, y)) / 2


def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    if len(array) == 0:
        return 0
    array = array.flatten()
    if np.amin(array) < 0:
        array -= np.amin(array)
    array += 0.0000001
    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


def count_empty_comments(comments):
    empty_comments = 0
    for comment in comments:
        if comment == "":
            empty_comments += 1
    return empty_comments


# --- Load model and prediction ---
def get_model():
    path = 'model.json'
    filename = pkg_resources.resource_filename(__name__, path)
    with open(filename, 'rb') as file:
        model = pickle.load(file)
    return model


def predict(model, df):
    df = (
        df
        .assign(
            prediction=lambda x: np.where(model.predict(
                x[['comments', 'empty comments', 'patterns', 'dispersion']]) == 1, 'Bot', 'Human')
        )
    )
    return df


# --- Thread and progress ---
def task(data):
    author, group, max_comments, params = data
    group = group[:max_comments]
    clustering = DBSCAN(eps=params['eps'], min_samples=1, metric='precomputed')
    items = compute_distance(getattr(group, params['source']), params['func'])
    clusters = clustering.fit_predict(items)
    empty_comments = np.count_nonzero(group['empty'])

    return (
        author,
        len(group),
        empty_comments,
        len(np.unique(clusters)),
        gini(items[np.tril(items).astype(bool)]),
    )


def run_function_in_thread(pbar, function, max_value, args=[], kwargs={}):
    ret = [None]

    def myrunner(function, ret, *args, **kwargs):
        ret[0] = function(*args, **kwargs)

    thread = threading.Thread(target=myrunner, args=(function, ret) + tuple(args), kwargs=kwargs)
    thread.start()
    while thread.is_alive():
        thread.join(timeout=.1)
        if(pbar.n < max_value - .3):
            pbar.update(.1)
    pbar.n = max_value
    return ret[0]


def progress(repository, accounts, exclude, date, verbose, min_comments, max_comments, apikey, output_type, only_predicted):
    download_progress = tqdm(
        total=25, desc='Downloading comments', smoothing=.1,
        bar_format='{desc}: {percentage:3.0f}%|{bar}', leave=False)
    comments = run_function_in_thread(
        download_progress, process_comments, 25,
        args=[repository, accounts, date, min_comments, max_comments, apikey])
    download_progress.close()

    if comments is None:
        raise BodeghaError('Download failed please check stack trace and resolve the issues (401: Unauthorized means your api key is not a valid key).')

    if len(comments) < 1:
        raise BodeghaError('Available comments are not enough to predict the type of accounts')

    df = (
        comments
        [comments['author'].isin(
            comments
            .groupby('author', as_index=False)
            .count()[lambda x: x['body'] >= min_comments]['author'].values
        )]
        .sort_values('created_at', ascending=False)
        .groupby('author').head(max_comments)
    )


    if len(exclude) > 0:
        df = df[~df["author"].isin(exclude)]
        
    if len(accounts) > 0:
        df = df[lambda x: x['author'].isin(accounts)]

    if(len(df) > 1):
#         raise BodeghaError('There are not enough comments in the selected time period to\
# predict the type of accounts. At least 10 comments is required for each account.')

        inputs = []
        for author, group in df.groupby('author'):
            inputs.append(
                (
                    author,
                    group.copy(),
                    max_comments,
                    {'func': average_jac_lev, 'source': 'body', 'eps': 0.5}
                )
            )

        data = []
        with Pool() as pool:
            for result in tqdm(
                    pool.imap_unordered(task, inputs),
                    desc='Computing features',
                    total=len(inputs),
                    smoothing=.1,
                    bar_format='{desc}: {percentage:3.0f}%|{bar}',
                    leave=False):
                data.append(result)

        result = pandas.DataFrame(
            data=data, columns=['account', 'comments', 'empty comments', 'patterns', 'dispersion'])

        prediction_progress = tqdm(
            total=25, smoothing=.1, bar_format='{desc}: {percentage:3.0f}%|{bar}', leave=False)
        tasks = ['Loading model', 'Making prediction', 'Exporting result']
        prediction_progress.set_description(tasks[0])
        model = run_function_in_thread(prediction_progress, get_model, 5)
        if model is None:
            raise BodeghaError('Could not load the model file')

        result = (
            result
            .assign(
                prediction=lambda x: np.where(model.predict(
                    x[['comments', 'empty comments', 'patterns', 'dispersion']]) == 1, 'Bot', 'Human')
            )
        )
        
        del model
        result = result.sort_values(['prediction', 'account']).assign(patterns= lambda x: x['patterns'].astype('Int64'))
        prediction_progress.close()
    else:
        result=pandas.DataFrame(columns = ['account', 'comments', 'empty comments', 'patterns', 'dispersion'])

    if only_predicted == True:
        result = result.append(  
            (
                comments[lambda x: ~x['author'].isin(result['account'])][['author','body']]
                .groupby('author', as_index=False)
                .count()
                .assign(
                    emptycomments=np.nan,
                    patterns=np.nan,
                    dispersion=np.nan,
                    prediction="Unknown",
                )
                .rename(columns={'author':'account','body':'comments','emptycomments':'empty comments'})
            ),ignore_index=True,sort=True)
        
        for identity in (set(accounts) - set(result['account'])):
            result = result.append({
                'account': identity,
                'comments':np.nan,
                'empty comments':np.nan,
                'patterns':np.nan,
                'dispersion':np.nan,
                'prediction':"Not found",
            },ignore_index=True,sort=True)
    
    if verbose is False:
        result = result.set_index('account')[['prediction']]
    else:
        result = (
            result
            .set_index('account')
            [['comments', 'empty comments', 'patterns', 'dispersion','prediction']]
        )

    if output_type == 'json':
        return (result.reset_index().to_json(orient='records'))
    elif output_type == 'csv':
        return (result.to_csv())
    else:
        return (result)


# --- cli ---
def arg_parser():
    parser = argparse.ArgumentParser(description='BoDeGHa - Bot detection in Github')
    parser.add_argument('repository', help='Name of a repository on GitHub ("owner/repo")')
    parser.add_argument(
        '--accounts', metavar='ACCOUNT', required=False, default=list(), type=str, nargs='*',
        help='User login of one or more accounts. Example: \
--accounts mehdijuliani melgibson tomgucci')
    parser.add_argument(
        '--exclude', metavar='ACCOUNT', required=False, default=list(), type=str, nargs='*',
        help='List of accounts to be excluded in the analysis. Example: \
--exclude mehdijuliani melgibson tomgucci')
    
    parser.add_argument(
        '--start-date', type=str, required=False,
        default=None, help='Starting date of comments to be considered')
    parser.add_argument(
        '--verbose', action="store_true", required=False, default=False,
        help='To have verbose output result')
    parser.add_argument(
        '--min-comments', type=int, required=False, default=10,
        help='Minimum number of comments to analyze an account')
    parser.add_argument(
        '--max-comments', type=int, required=False, default=100,
        help='Maximum number of comments to be used (default=100)')
    parser.add_argument(
        '--key', metavar='APIKEY', required=True, type=str, default='',
        help='GitHub APIv4 key to download comments from GitHub GraphQL API')
    parser.add_argument(
        '--only-predicted', action="store_false", required=False, default=True,
        help='Only list accounts that the prediction is available.')
    
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('--text', action='store_true', help='Print results as text.')
    group2.add_argument('--csv', action='store_true', help='Print results as csv.')
    group2.add_argument('--json', action='store_true', help='Print results as json.')

    return parser.parse_args()


def cli():
    args = arg_parser()

    date = datetime.now()+relativedelta(months=-6)
    if args.start_date is not None:
        date = dateutil.parser.parse(args.start_date)

    if args.min_comments > args.max_comments:
        sys.exit('The minimum number of comments should be less than the maximum number of comments.')
    else:
        min_comments = args.min_comments
        max_comments = args.max_comments

    if args.key == '' or len(args.key) < 35:
        sys.exit('A GitHub personal access token is required to start the process. \
Please read more about it in the repository readme file.')
    else:
        apikey = args.key

    if args.csv:
        output_type = 'csv'
    elif args.json:
        output_type = 'json'
    else:
        output_type = 'text'

    try:
        with pandas.option_context('display.max_rows', None, 'display.max_columns', None):
            print(
                progress(
                    args.repository,
                    args.accounts,
                    args.exclude,
                    date,
                    args.verbose,
                    min_comments,
                    max_comments,
                    apikey,
                    output_type,
                    args.only_predicted,
                ))
    except BodeghaError as e:
        sys.exit(e)


if __name__ == '__main__':
    cli()