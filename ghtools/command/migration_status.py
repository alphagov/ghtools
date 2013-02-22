from __future__ import print_function
import json

from argh import *
from ghtools import cli
from ghtools.github import Organisation
from collections import defaultdict
import csv
import sys


@arg('src', help='The source organisation in question')
@arg('dest', help='The destination organisation in question')
def show_migration_status(args):
    """
    List authorised repos for teams
    """
    with cli.catch_api_errors():
        src = Organisation(args.src)
        dest = Organisation(args.dest)

    repos_dest = list(dest.list_repos())
    lod = [ ] # "list of dicts"

    for repo_src in src.list_repos():
            (migrated,repo_dest) = exists_in(repo_src, repos_dest)
            dest_private = str(repo_dest['private']) if migrated else 'N/A'
            lod.append({
                'NAME':repo_src['name'], 
                'MIGRATED':str(migrated), 
                'SRC_PRIVATE':str(repo_src['private']),
                'DEST_PRIVATE':dest_private})

    # TODO:
    # Technically you should be able to do something like:
    # query_lod(lod, sort_keys=('MIGRATED', 'NAME'))) but I can't seem
    # to get it to work
    query_results = query_lod(lod, lambda r:r['MIGRATED']=='True' )

    pattern = '{0:45s} {1:10s} {2:11s} {3:11s}'
    inputs = ['NAME', 'MIGRATED', 'SRC_PRIVATE', 'DEST_PRIVATE']

    print(pattern.format(*inputs))
    for row in query_results:
        print(pattern.format(*[row[r] for r in inputs]))


def exists_in(repo_src, repos):
    for repo in repos: 
        if repo['name'] == repo_src['name']:
            return (True,repo)
    return (False,None)


def query_lod(lod, filter=None, sort_keys=None):
    if filter is not None:
        lod = (r for r in lod if filter(r))
    if sort_keys is not None:
        lod = sorted(lod, key=lambda r:[r[k] for k in sort_keys])
    else:
        lod = list(lod)
        return lod


def lookup_lod(lod, **kw):
    for row in lod:
        for k,v in kw.iteritems():
            if row[k] != str(v): break
        else:
                return row
    return None


def main():
    dispatch_command(show_migration_status)


if __name__ == '__main__':
    main()
