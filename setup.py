import os
from setuptools import setup, find_packages

from ghtools import __version__

requirements = [
    'requests==2.2.1',
    'argh==0.23.0'
]

python_scripts = [
    'browse',
    'list-members',
    'login',
    'migrate-project',
    'migrate-wiki',
    'migrate-teams',
    'org',
    'repo',
    'status',
]

HERE = os.path.dirname(__file__)
try:
    long_description = open(os.path.join(HERE, 'README.rst')).read()
except:
    long_description = None

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
    long_description=long_description,
    license='MIT',
    keywords='sysadmin git github api',

    install_requires=requirements,

    entry_points={
        'console_scripts': [
            'gh-{0}=ghtools.command.{1}:main'.format(s, s.replace('-', '_')) for s in python_scripts
        ]
    }
)
