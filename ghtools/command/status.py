from __future__ import print_function

import json
import logging

from argh import ArghParser, arg
from ghtools import cli
from ghtools.github.repo import Repo

log = logging.getLogger(__name__)
parser = ArghParser(description="Set commit/branch build status")


@arg('repo', help='Repository identifier (e.g. joebloggs/myapp, enterprise:mycorp/myrepo)')
@arg('sha', help='Git SHA1')
@arg('state', help='State to attach', choices=['pending', 'success', 'error', 'failure'])
@arg('-d', '--description', help='Status description')
@arg('-u', '--url', help='URL linking to status details')
@arg('-c', '--context', help='Label to differentiate this status from the status of other systems')
def status(args):
    """
    Set build status for a commit on GitHub
    """
    repo = Repo(args.repo)

    payload = {'state': args.state}

    if args.description is not None:
        payload['description'] = args.description

    if args.url is not None:
        payload['target_url'] = args.url

    if args.context is not None:
        payload['context'] = args.context

    with cli.catch_api_errors():
        res = repo.set_build_status(args.sha, payload)

    print(json.dumps(res.json(), indent=2))
parser.set_default_command(status)


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
