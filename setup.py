from os import path
from setuptools import setup
from codecs import open # To use a consistent encoding


__package__ = 'bodegha'
__version__ = '1.0.3'
__licence__ = 'LGPL3'
__maintainer__ = 'Mehdi Golzadeh'
__email__ = 'golzadeh.mehdi@gmail.com'
__url__ = 'https://github.com/mehdigolzadeh/BoDeGHa'
__description__ = 'BoDeGHA - Bot detector an automated tool to identify bots in GitHub by analysing comments patterns'
__long_description__ = 'This tool accepts the name of a GitHub repository and a GitHub API key and computes its output in three steps.\\\
The first step consists of downloading all comments from the specified GitHub repository thanks to GitHub GraphQL API. This step results in a list of commenters and their corresponding comments.\\\
The second step consists of computing the number of comments, empty comments, comment patterns, and inequality between the number of comments within patterns.\\\
The third step simply applies the model we developed on these examples and outputs the prediction made by the model.'
__classifiers__=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
__requirement__ = [
        'python-dateutil >= 2.7.5',
        'pandas >= 0.23.4',
        'scikit-learn == 1.5.0',
        'argparse >= 1.1',
        'tqdm >= 4.41.1',
        'urllib3 >= 1.25',
        'python-levenshtein >= 0.12.2',
        'numpy >= 1.17.4',
]

setup(
    name=__package__,

    version=__version__,

    description= __description__,
    long_description=__long_description__,

    url=__url__,

    maintainer=__maintainer__,
    maintainer_email=__email__,

    license=__licence__,

    classifiers=__classifiers__,

    keywords='github bot account comment',

    install_requires = __requirement__,

    include_package_data = True,
    packages = ['.'],

    entry_points={
        'console_scripts': [
            'bodegha=bodegha:cli',
        ]
    },

    py_modules=['bodegha'],
    zip_safe=True,
)
