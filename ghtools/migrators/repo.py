import subprocess
import logging
import os

from ghtools.api import APIError
from ghtools.ssh_key import SSHKey

log = logging.getLogger(__name__)

def migrate(src, dst, name):
	key = SSHKey()
	key.create()

	try:
		key.add_host(src.hostname)
		key.add_host(dst.hostname)

		try:
			src.add_public_key("ghtools migration tool", key.public_key)
			dst.add_public_key("ghtools migration tool", key.public_key)
		except APIError:
			pass

		run("mkdir -p repos")
		if not os.path.exists(os.path.join("repos", name)):
			run("git clone --bare ghtools.{0}:{1} repos/{2}".format(dst.hostname, dst.full_name(name), name))
			run("cd repos/{0} && git remote add upstream ghtools.{1}:{2}".format(name, src.hostname, src.full_name(name)))

		run("cd repos/{0} && git fetch upstream".format(name))
		run("cd repos/{0} && git push --mirror origin".format(name))

		branches = filter(None, map(str.strip, run('cd repos/{0} && git branch -r'.format(name), output=True).split("\n")))
		for branch in branches:
			b = branch.split('/')[1]
			run('cd repos/{0} && git push --force origin {1}:refs/heads/{2}'.format(name, branch, b))
	except APIError as e:
		print(e.response.text)
		raise
	finally:
		if key.exists:
			src.remove_public_key(key.public_key)
			dst.remove_public_key(key.public_key)

			key.remove()


def run(command, output=False):
	log.debug(command)
	if output:
		return subprocess.check_output(command, shell=True)
	else:
		return subprocess.call(command, shell=True)

