from os import path
from setuptools import setup
from codecs import open # To use a consistent encoding


__package__ = 'botdetector'
__version__ = '0.0.0'
__licence__ = 'LGPL3'
__maintainer__ = 'Mehdi Golzadeh'
__email__ = 'golzadeh.mehdi@gmail.com'
__url__ = 'https://github.com/MehdiGolzadeh/BotDetector'
__description__ = 'BotDetector - A library to identify bot by analysing their comments'
__long_description__ = ''
__classifiers__=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        # 'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Python Software Foundation License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
__requirement__ = ['not listed yet']


setup(
    name=__package__,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=__version__,

    description= __description__,
    long_description=long_description,

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
    keywords='github,bot,account,comment',

    # You can just specify the packages manually here if your project is simple.
    # Or you can use find_packages().
    packages=[__package__],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires = __requirement__,

    # Tests
    #
    # Tests must be wrapped in a unittest test suite by either a
    # function, a TestCase class or method, or a module or package
    # containing TestCase classes. If the named suite is a package,
    # any submodules and subpackages are recursively added to the
    # overall test suite.
    test_suite = 'no test suite',

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

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #
    # entry_points={
    #     'console_scripts': [
    #         'command=module:main',
    #     ],
    # },
)