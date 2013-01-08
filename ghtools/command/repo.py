from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with GitHub repos")
parser.add_argument('-n', '--nickname', default='public', help='GitHub instance nickname')
parser.add_argument('repo', help='Repo name, e.g. defunkt/resque')


def delete(args):
    """
    Delete the specified repository
    """
    c = GithubAPIClient(nickname=args.nickname)

    res = c.delete('/repos/{0}'.format(args.repo))
    res.raise_for_status()


def get(args):
    """
    Print the JSON representation of the specified repository to STDOUT
    """
    c = GithubAPIClient(nickname=args.nickname)

    res = c.get('/repos/{0}'.format(args.repo))
    return json.dumps(res.json, indent=2)


parser.add_commands([delete, get])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
