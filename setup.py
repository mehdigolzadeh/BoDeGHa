from os import path
from setuptools import setup
from codecs import open # To use a consistent encoding


__package__ = 'bodega'
__version__ = '0.2.0'
__licence__ = 'LGPL3'
__maintainer__ = 'Mehdi Golzadeh'
__email__ = 'golzadeh.mehdi@gmail.com'
__url__ = 'https://github.com/mehdigolzadeh/BoDeGa'
__description__ = 'BoDeGA - Bot detector an automated tool to identify bots in GitHub by analysing comments patterns'
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
    ]
__requirement__ = [
        'python-dateutil >= 2.7.5',
        'pandas >= 0.23.4',
        'scikit-learn >= 0.22',
        'argparse >= 1.1',
        'tqdm >= 4.41.1',
        'urllib3 >= 1.25',
        'python-levenshtein >= 0.12.0',
]

datadir = os.path.join('share','data')
datafiles = [(d, [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]


setup(
    name=__package__,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=__version__,

    description= __description__,
    long_description=__long_description__,

    # The project's main homepage.
    url=__url__,

    # Maintainer details (this is a backport)
    maintainer=__maintainer__,
    maintainer_email=__email__,

    # Choose your license
    license=__licence__,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=__classifiers__,

    # What does your project relate to?
    keywords='github bot account comment',

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires = __requirement__,

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     '': ['*.rst']
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    ## data_files=[('my_data', ['data/data_file'])],

    data_files =[('bodega_data', ['model.pkl'])],

    entry_points={
        'console_scripts': [
            'bodega=bodega:cli',
        ]
    },

    py_modules=['bodega'],
    zip_safe=True,
)