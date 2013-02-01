from __future__ import print_function

import logging

from argh import *
from ghtools.api import GithubOrganisation
from ghtools import migrators

@arg('src', help='Migration source')
@arg('dst', help='Migration destination')
def migrate_org(args):
	src = GithubOrganisation.create(args.src)
	dst = GithubOrganisation.create(args.dst)

	app_name = "feedback"

	migrators.project.migrate(src, dst, app_name)
	migrators.repo.migrate(src, dst, app_name)
	migrators.issues.migrate(src, dst, app_name)

def main():
	dispatch_command(migrate_org)

if __name__ == '__main__':
	main()