import subprocess
import logging

from ghtools.ssh_key import SSHKey

log = logging.getLogger(__name__)

def migrate(src, dst, name):
	key = SSHKey()
	key.create()

	try:
		key.add_host(src.hostname)
		key.add_host(dst.hostname)

		src.add_public_key("ghtools migration tool", key.public_key)
		dst.add_public_key("ghtools migration tool", key.public_key)

		run("mkdir repos")
		run("git clone ghtools.{0}:{1} repos/{2}".format(dst.hostname, dst.full_name(name), name))
		run("cd repos/{0} && git remote add upstream ghtools.{1}:{2}".format(name, dst.hostname, src.full_name(name)))
		run("cd repos/{0} && git fetch --tags upstream".format(name))

		run("cd repos/{0} && git merge upstream/master".format(name))
		run("cd repos/{0} && git push origin".format(name))

	finally:
		if key.exists:
			src.remove_public_key(key.public_key)
			dst.remove_public_key(key.public_key)

			key.remove()


def run(command):
	log.debug(command)
	return subprocess.call(command, shell=True)

