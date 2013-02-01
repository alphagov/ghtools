from setuptools import setup, find_packages

from ghtools import __version__

requirements = [
    'requests==0.14.2',
    'argh==0.17.2'
]

python_scripts = [
    'browse',
    'list-members',
    'login',
    'org',
    'repo',
    'sync-org',
    'migrate-project'
]

setup(
    name='ghtools',
    version=__version__,
    packages=find_packages(exclude=['test*']),

    # metadata for upload to PyPI
    author='Nick Stenning',
    author_email='nick@whiteink.com',
    maintainer='Government Digital Service',
    url='https://github.com/alphagov/ghtools',

    description='ghtools: tools for interacting with the GitHub API',
    license='MIT',
    keywords='sysadmin git github api',

    install_requires=requirements,

    entry_points={
        'console_scripts': [
            'gh-{0}=ghtools.command.{1}:main'.format(s, s.replace('-', '_')) for s in python_scripts
        ]
    }
)
