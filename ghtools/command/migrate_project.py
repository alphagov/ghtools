from __future__ import print_function

import logging

from argh import arg, dispatch_command
from ghtools.github.organisation import Organisation
from ghtools.github.repo import Repo
from ghtools import migrators, cli

log = logging.getLogger(__name__)


@arg('src', help='Migration source identifier (e.g. rails/rails)')
@arg('dst', help='Migration destination identifier (e.g. enterprise:rails/rails)')
def migrate_project(args):
    """
    Migrate a Github project from one Github instance to another.

    Migration includes:
        - Project metadata
        - Git repository
        - Issues & pull requests
        - Comments
        - Hooks

    WARNING: This will copy the git repository verbatim. Any commits on the
    target repository that are not also on the source will be lost.

    Note: All issues and comments will be migrated as the target user with
    links back to the source Github instance.
    """
    with cli.catch_api_errors():
        src_org = Organisation(args.src)
        dst_org = Organisation(args.dst)
        src = Repo(args.src)
        dst = Repo(args.dst)

        # Create the repo object
        log.info("Migrating %s to %s -> creating repo", src, dst)
        project = src_org.get_repo(src.repo)
        project['name'] = dst.repo
        dst_org.create_repo(project)

        # Migrate repo data
        migrators.repo.migrate(src, dst)
        migrators.issues.migrate(src, dst)
        migrators.comments.migrate(src, dst)
        migrators.hooks.migrate(src, dst)


def main():
    dispatch_command(migrate_project)


if __name__ == '__main__':
    main()
