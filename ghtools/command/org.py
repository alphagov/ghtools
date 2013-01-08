from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with a GitHub organisation")
parser.add_argument('-n', '--nickname', default='public', help='GitHub instance nickname')

@arg('-j', '--json', default=False, help='Print full JSON representations')
@arg('org', help='Organisation name')
def repos(args):
    """
    Print a list of organisation repositories
    """
    c = GithubAPIClient(nickname=args.nickname)
    for repo in c.paged_get('/orgs/{0}/repos'.format(args.org)):
        if args.json:
            print(json.dumps(repo, indent=2))
        else:
            print(repo['name'])

@arg('-j', '--json', default=False, help='Print full JSON representations')
@arg('org', help='Organisation name')
def members(args):
    """
    Print a list of organisation members
    """
    c = GithubAPIClient(nickname=args.nickname)
    for repo in c.paged_get('/orgs/{0}/members'.format(args.org)):
        if args.json:
            print(json.dumps(repo, indent=2))
        else:
            print(repo['login'])

parser.add_commands([repos, members])

def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
