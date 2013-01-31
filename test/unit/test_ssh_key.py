from ..helpers import *
import shutil

from ghtools.ssh_key import SSHKey

class TestSSHKey(object):
	def test_create(self):
		key = SSHKey()

		assert_true(key.root.endswith('.ssh'))

	def setup(self):
		self.key = SSHKey(root="/var/tmp/ghtools-ssh")

	def teardown(self):
		if os.path.exists(self.key.root):
			shutil.rmtree(self.key.root)

	def test_root_path(self):
		assert_equal(self.key.root, "/var/tmp/ghtools-ssh")
		assert_true(os.path.exists(self.key.root))

	def test_private_key_file(self):
		assert_equal(self.key.private_key_file, "/var/tmp/ghtools-ssh/ghtools-key")

	def test_public_key_file(self):
		assert_equal(self.key.public_key_file, "/var/tmp/ghtools-ssh/ghtools-key.pub")

	def test_public_key(self):
		self.key.create()

		contents = read_file_contents(self.key.public_key_file)

		assert_equal(contents, self.key.public_key)

	def test_create_creates_key_pair(self):
		self.key.create()

		assert_true(os.path.exists(self.key.private_key_file))
		assert_true(os.path.exists(self.key.public_key_file))

	def test_create_does_not_regenerate_existing_key_pair(self):
		self.key.create()
		contents = self.key.public_key

		self.key.create()
		new_contents = self.key.public_key

		assert_equal(contents, new_contents)

	def test_exists(self):
		assert_false(self.key.exists)
		self.key.create()
		assert_true(self.key.exists)

	def test_config_path(self):
		assert_equal(self.key.config_path, "/var/tmp/ghtools-ssh/config")

	def test_add_host(self):
		self.key.create()

		contents = read_file_contents(self.key.config_path)

		assert_true("# start ghtools.myhost" not in contents)

		self.key.add_host("myhost")

		contents = read_file_contents(self.key.config_path)

		host_block = "# start ghtools.myhost\n" \
		           + "Host ghtools.myhost\n" \
		           + "HostName myhost\n" \
		           + "User git\n" \
		           + "IdentityFile /var/tmp/ghtools-ssh/ghtools-key\n" \
		           + "# end ghtools.myhost\n"

		assert_true(host_block in contents)

	def test_add_host_retains_existing_configuration(self):
		self.key.create()

		original = "Host foo\nHostname foo.bar.com\nUser git\n"
		write_file_contents(self.key.config_path, original)

		self.key.add_host("myhost")

		assert_true(original in read_file_contents(self.key.config_path))

	def test_add_host_replaces_existing_host_section(self):
		self.key.create()
		self.key.add_host("myhost")
		self.key.add_host("myhost")

		assert_equal(read_file_contents(self.key.config_path).count("# start ghtools.myhost"), 1)

	def test_remove(self):
		self.key.create()
		self.key.add_host("myhost")
		self.key.add_host("myotherhost")
		self.key.remove()

		print(read_file_contents(self.key.config_path))

		assert_false("myhost" in read_file_contents(self.key.config_path))


def read_file_contents(path):
	try:
		with open(path, "r") as f:
			return f.read()
	except IOError:
		return ""

def write_file_contents(path, contents):
	with open(path, "w+") as f:
		f.write(contents)

