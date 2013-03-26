from __future__ import print_function

import json
import logging

from argh import ArghParser
from ghtools import cli
from ghtools.github.repo import Repo

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with GitHub repos")
parser.add_argument('repo', help='Repo identifier, e.g. defunkt/resque, enterprise:mycorp/myproj')


def delete(args):
    """
    Delete the specified repository
    """
    repo = Repo(args.repo)

    with cli.catch_api_errors():
        repo.delete()
parser.add_commands([delete])


def get(args):
    """
    Print the JSON representation of the specified repository to STDOUT
    """
    repo = Repo(args.repo)

    with cli.catch_api_errors():
        return json.dumps(repo.get(), indent=2)
parser.add_commands([get])

def create(args):
    """
    Create a repo with specified name
    """
    repo = Repo(args.repo)

    with cli.catch_api_errors():
        return repo.create()
parser.add_commands([create])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
