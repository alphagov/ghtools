from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient

log = logging.getLogger(__name__)

@arg('-n', '--nickname', default='public', help='GitHub instance nickname')
@arg('repo', help='Repo name, e.g. defunkt/resque')
def get(args):
    """
    Print the JSON representation of the specified repository to STDOUT
    """
    c = GithubAPIClient(nickname=args.nickname)
    owner, repo = args.repo.rsplit('/', 2)
    res = c.repo(owner, repo)
    return json.dumps(res, indent=2)

parser = ArghParser(description="Interact with GitHub repos")
parser.add_commands([get])

def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
