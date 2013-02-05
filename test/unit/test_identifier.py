from ..helpers import *

from ghtools.identifier import Identifier


class TestIdentifier(object):

    def test_org_only(self):
        i = Identifier.from_string('myorg')
        assert_equal(i.github, 'public')
        assert_equal(i.org, 'myorg')
        assert_equal(i.repo, None)

    def test_explicit_org(self):
        i = Identifier.from_string('foo:myorg')
        assert_equal(i.github, 'foo')
        assert_equal(i.org, 'myorg')
        assert_equal(i.repo, None)

    def test_implicit_repo(self):
        i = Identifier.from_string('myorg/myrepo')
        assert_equal(i.github, 'public')
        assert_equal(i.org, 'myorg')
        assert_equal(i.repo, 'myrepo')

    def test_explicit_repo(self):
        i = Identifier.from_string('foo:myorg/myrepo')
        assert_equal(i.github, 'foo')
        assert_equal(i.org, 'myorg')
        assert_equal(i.repo, 'myrepo')

    def test_str(self):
        i = Identifier.from_string('foo:myorg/myrepo')
        assert_equal(str(i), 'foo:myorg/myrepo')

    def test_str_public(self):
        i = Identifier.from_string('myorg/myrepo')
        assert_equal(str(i), 'myorg/myrepo')

    def test_str_repoless(self):
        i = Identifier.from_string('foo:myorg')
        assert_equal(str(i), 'foo:myorg')
