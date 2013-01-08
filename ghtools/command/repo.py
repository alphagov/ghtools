from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with GitHub repos")
parser.add_argument('-n', '--nickname', default='public', help='GitHub instance nickname')

@arg('repo', help='Repo name, e.g. defunkt/resque')
def delete(args):
    """
    Delete the specified repository
    """
    c = GithubAPIClient(nickname=args.nickname)
    owner, repo = args.repo.rsplit('/', 2)

    res = c.delete('/repos/{0}/{1}'.format(owner, repo))
    res.raise_for_status()

@arg('repo', help='Repo name, e.g. defunkt/resque')
def get(args):
    """
    Print the JSON representation of the specified repository to STDOUT
    """
    c = GithubAPIClient(nickname=args.nickname)
    owner, repo = args.repo.rsplit('/', 2)

    res = c.get('/repos/{0}/{1}'.format(owner, repo))
    return json.dumps(res.json, indent=2)

parser.add_commands([delete, get])

def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
