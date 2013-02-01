import os
import subprocess
import logging

log = logging.getLogger(__name__)

class SSHKey(object):
	def __init__(self, root="~/.ssh"):
		self.root = os.path.expanduser(root)

		if not os.path.exists(self.root):
			os.mkdir(self.root)

	def create(self):
		if not self.exists:
			keygen = "/usr/bin/ssh-keygen -f {0} -N '' -q"

			self._run(keygen.format(self.private_key_file))

	@property
	def private_key_file(self):
		return os.path.join(self.root, "ghtools-key")

	@property
	def public_key_file(self):
		return self.private_key_file + ".pub"

	@property
	def public_key(self):
		with open(self.public_key_file, "r") as f:
			return f.read()

	@property
	def exists(self):
		return os.path.exists(self.private_key_file)

	@property
	def config_path(self):
		return os.path.join(self.root, "config")

	def add_host(self, hostname):
		self._touch_config()
		
		lines = []
		in_host_block = False
		with open(self.config_path, "r") as f:
			for line in f.readlines():
				if not in_host_block and line.startswith("# start ghtools.{0}".format(hostname)):
					in_host_block = True

				if not in_host_block:
					lines.append(line.rstrip("\n"))

				if in_host_block and line.startswith("# end ghtools.{0}".format(hostname)):
					in_host_block = False

			lines.append("# start ghtools.{0}".format(hostname))
			lines.append("Host ghtools.{0}".format(hostname))
			lines.append("HostName {0}".format(hostname))
			lines.append("User git")
			lines.append("IdentityFile {0}".format(self.private_key_file))
			lines.append("# end ghtools.{0}".format(hostname))

		with open(self.config_path, "w+") as f:
			f.write("\n".join(lines) + "\n")


	def remove(self):
		self._touch_config()

		lines = []
		in_host_block = False
		with open(self.config_path, "r") as f:
			for line in f.readlines():
				if not in_host_block and line.startswith("# start ghtools."):
					in_host_block = True

				if not in_host_block:
					lines.append(line.rstrip("\n"))

				if in_host_block and line.startswith("# end ghtools."):
					in_host_block = False

		with open(self.config_path, "w+") as f:
			f.write("\n".join(lines) + "\n")

		os.remove(self.public_key_file)
		os.remove(self.private_key_file)

	def _touch_config(self):
		if not os.path.exists(self.config_path):
			with open(self.config_path, "w+") as f: f.write("")

	def _run(self, command):
		log.debug(command)
		return subprocess.call(command, shell=True)
