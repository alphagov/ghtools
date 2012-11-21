from __future__ import print_function

import logging

from argh import *
from ghtools.api import GithubAPIClient, ClientError, APIError

log = logging.getLogger(__name__)

def extract_keys(obj, keys):
    newobj = {}
    for k in keys:
        newobj[k] = obj[k]
    return newobj

def sync_repo(gh_client, org, repo):
    log.debug("Checking if %s/%s exists on %s", org, repo['name'], gh_client)

    try:
        r = gh_client.repo(org, repo['name'])
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            log.debug("%s/%s doesn't exist on %s, creating...", org, repo['name'], gh_client)
            create_repo(gh_client, org, repo)
        else:
            raise
    else:
        log.debug("%s/%s already exists on %s, skipping...", org, repo['name'], gh_client)

def create_repo(gh_client, org, repo):
    data = extract_keys(repo, [
        'name',
        'description',
        'homepage',
        'private',
        'has_issues',
        'has_wiki',
        'has_downloads'
    ])
    gh_client.org_repo_create(org, repo)
    log.info("Created %s/%s on %s", org, repo['name'], gh_client)

@arg('src', help='Sync source')
@arg('dst', help='Sync destination')
def sync_org(args):
    """
    Sync an organisation between two GitHub instances.

    The source and destination should be given in the format

       <nickname>:<org>

    For example, to sync the 'foocorp' organisation on the public GitHub to
    the 'foo' organisation on the GitHub with nickname 'internal', you would
    run

       %(prog)s public:foocorp internal:foo
    """

    src_nickname, src_org = args.src.rsplit(':', 2)
    dst_nickname, dst_org = args.dst.rsplit(':', 2)

    src = GithubAPIClient(nickname=src_nickname)
    dst = GithubAPIClient(nickname=dst_nickname)

    for repo in src.org_repos(src_org):
        sync_repo(dst, dst_org, repo)

def main():
    dispatch_command(sync_org)

if __name__ == '__main__':
    main()
