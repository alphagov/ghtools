from ghtools.api import GithubAPIClient

def make_client(identifier):
    """
    Make a GithubAPIClient suitable for interacting with the passed identifier
    """

    return GithubAPIClient(nickname=identifier.github)


