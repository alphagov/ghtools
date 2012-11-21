ghtools
=======

A set of commandline utilities to assist with manipulating GitHubs (plural).

Installation
------------

For the time being, I suggest you clone the repository, and do a::

    $ pip install -e .

Usage
-----

Simple usage::

    $ eval `gh-login`
    $ gh-repo get alphagov/ghtools

Multiple GitHubs: sync an organisation::

    $ export GITHUB_GHE_API_ROOT=https://git.internal/api/v3
    $ eval `gh-login -n public`
    $ eval `gh-login -n ghe`
    $ gh-sync-org public:alphagov ghe:alphagov

NB: the sync doesn't do everything it should or even close at the moment. It
will simply create repositories (metadata only) if they don't exist.

License
-------

``ghtools`` is released under the MIT license, a copy of which can be found
in ``LICENSE``.
