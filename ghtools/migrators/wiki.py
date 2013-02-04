import subprocess
import logging
import os

from ghtools.api import GithubAPIError
from ghtools.ssh_key import SSHKey

log = logging.getLogger(__name__)


def migrate(src, dst, name):
    if src.get_project(name).json['has_wiki']:
        dst.client.patch('/repos/{0}'.format(dst.full_name(name)), data={'name': name, 'has_wiki': True})

        key = SSHKey()
        key.create()

        try:
            key.add_host(src.hostname)
            key.add_host(dst.hostname)

            try:
                src.add_public_key("ghtools migration tool", key.public_key)
                dst.add_public_key("ghtools migration tool", key.public_key)
            except GithubAPIError:
                pass

            run("mkdir -p repos")

            if not os.path.exists(os.path.join("repos", "{0}.wiki".format(name))):
                run("git clone --bare ghtools.{0}:{1}.wiki repos/{2}.wiki".format(dst.hostname, dst.full_name(name), name))
                run("cd repos/{0}.wiki && git remote add upstream ghtools.{1}:{2}.wiki".format(name, src.hostname, src.full_name(name)))

            run("cd repos/{0}.wiki && git fetch upstream".format(name))
            run("cd repos/{0}.wiki && git push --mirror origin".format(name))
            run("cd repos/{0}.wiki && git push --force origin upstream/master:refs/heads/master".format(name))
        except GithubAPIError as e:
            print(e.response.text)
            raise
        finally:
            if False and key.exists:
                src.remove_public_key(key.public_key)
                dst.remove_public_key(key.public_key)

                key.remove()


def run(command, output=False):
    log.debug(command)
    if output:
        return subprocess.check_output(command, shell=True)
    else:
        return subprocess.call(command, shell=True)
