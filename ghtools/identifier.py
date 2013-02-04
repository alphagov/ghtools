from collections import namedtuple

_Identifier = namedtuple('Identifier', 'github org repo')

class Identifier(_Identifier):
    """

    A simple identifier of an object in the GitHub API, usually created from a
    string passed in on the command line.

    Users can reference a repository on a specific GitHub using the form::

        <github_name>:<org_name>/<repo_name>

    Where ``github_name`` is optional (defaulting to 'public').

    The repository can also be omitted in order to refer to an Organisation::

        <github_name>:<org_name>

    Again, ``github_name`` is optional.

    """

    @classmethod
    def from_string(cls, identstring):

        parts = identstring.split(':', 1)

        if len(parts) == 1:
            github = 'public'
            remainder = parts[0]
        else:
            github, remainder = parts

        parts = remainder.split('/', 1)

        if len(parts) == 1:
            org = parts[0]
            repo = None
        else:
            org, repo = parts

        return Identifier(github, org, repo)
