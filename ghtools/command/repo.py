from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient
from ghtools.identifier import Identifier

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with GitHub repos")
parser.add_argument('repo', help='Repo identifier, e.g. defunkt/resque, enterprise:mycorp/myproj')


def delete(args):
    """
    Delete the specified repository
    """
    ident = Identifier.from_string(args.repo)
    c = GithubAPIClient(nickname=ident.github)

    res = c.delete('/repos/{0}/{1}'.format(ident.org, ident.repo))
    res.raise_for_status()


def get(args):
    """
    Print the JSON representation of the specified repository to STDOUT
    """
    ident = Identifier.from_string(args.repo)
    c = GithubAPIClient(nickname=ident.github)

    res = c.get('/repos/{0}/{1}'.format(ident.org, ident.repo))
    return json.dumps(res.json, indent=2)


parser.add_commands([delete, get])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
