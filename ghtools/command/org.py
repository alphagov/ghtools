from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient
from ghtools.identifier import Identifier

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with a GitHub organisation")
parser.add_argument('org', help='Organisation identifier (e.g. rails, enterprise:mycorp)')
parser.add_argument('-j', '--json', default=False, help='Print full JSON representations')


def repos(args):
    """
    Print a list of organisation repositories
    """
    ident = Identifier.from_string(args.org)
    c = GithubAPIClient(nickname=ident.github)
    for repo in c.paged_get('/orgs/{0}/repos'.format(ident.org)):
        if args.json:
            print(json.dumps(repo, indent=2))
        else:
            print(repo['name'])


def members(args):
    """
    Print a list of organisation members
    """
    ident = Identifier.from_string(args.org)
    c = GithubAPIClient(nickname=ident.github)
    for repo in c.paged_get('/orgs/{0}/members'.format(ident.org)):
        if args.json:
            print(json.dumps(repo, indent=2))
        else:
            print(repo['login'])


parser.add_commands([repos, members])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
