from __future__ import print_function

import json
import logging

from argh import *
from ghtools.api import GithubAPIClient

log = logging.getLogger(__name__)
parser = ArghParser(description="Set commit/branch build status")

@arg('-n', '--nickname', default='public', help='GitHub instance nickname')
@arg('repo', help='Repository name (e.g. "joebloggs/myapp")')
@arg('sha', help='Git SHA1')
@arg('state', help='State to attach', choices=['pending', 'success', 'error', 'failure'])
@arg('-d', '--description', help='Status description')
@arg('-u', '--url', help='URL linking to status details')
def status(args):
    """
    Set build status for a commit on GitHub
    """
    c = GithubAPIClient(nickname=args.nickname)

    payload = { 'state': args.state }

    if args.description is not None:
        payload['description'] = args.description

    if args.url is not None:
        payload['target_url'] = args.url

    res = c.post('/repos/{0}/statuses/{1}'.format(args.repo, args.sha), data=payload)

    print(json.dumps(res.json, indent=2))


def main():
    dispatch_command(status)

if __name__ == '__main__':
    main()
