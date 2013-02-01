from __future__ import print_function

import logging

from argh import *
from ghtools.api import GithubOrganisation
from ghtools import migrators

@arg('src',     help='Migration source')
@arg('dst',     help='Migration destination')
@arg('project', help='Project to be migrated')
def migrate_project(args):
	src = GithubOrganisation.create(args.src)
	dst = GithubOrganisation.create(args.dst)


	migrators.project.migrate(src, dst, args.project)
	migrators.repo.migrate(src, dst, args.project)
	migrators.issues.migrate(src, dst, args.project)
	migrators.comments.migrate(src, dst, args.project)
	migrators.hooks.migrate(src, dst, args.project)
	# migrators.wiki.migrate(src, dst, args.project) # The wiki has to be visted on the target to create it.

def main():
	dispatch_command(migrate_project)

if __name__ == '__main__':
	main()