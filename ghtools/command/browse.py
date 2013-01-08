from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient

log = logging.getLogger(__name__)
parser = ArghParser(description="Browse the GitHub API")

@arg('-n', '--nickname', default='public', help='GitHub instance nickname')
@arg('url', help='URL to browse')
def browse(args):
    """
    Print the GitHub API response at the given URL
    """
    c = GithubAPIClient(nickname=args.nickname)
    res = c.get(args.url)

    print('HTTP/1.1 {0} {1}'.format(res.status_code, res.reason))

    for k, v in res.headers.items():
        print("{0}: {1}".format(k, v))

    print()
    if res.json is not None:
        print(json.dumps(res.json, indent=2))
    else:
        print(res.content)

def main():
    dispatch_command(browse)

if __name__ == '__main__':
    main()
