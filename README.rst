ghtools
=======

A set of commandline utilities for interacting with the GitHub or GitHub
Enterprise API.

.. image:: https://travis-ci.org/alphagov/ghtools.png?branch=master
   :target: https://travis-ci.org/alphagov/ghtools

Installation
------------

``ghtools`` is available on PyPI_ and can be installed using pip_::

    $ pip install ghtools

.. _PyPI: http://pypi.python.org/pypi
.. _pip: http://www.pip-installer.org/
    
Usage
-----

Simple usage::

    $ eval `gh-login`
    $ gh-repo alphagov/ghtools get
    $ gh-org alphagov members

``ghtools`` is not a monolithic program. Instead, it comes with a number of
scripts which each perform very specific tasks. The aim is for these scripts
to be composable, allowing you to pipe their data to and from other unix tools
(``grep``, ``sort``, ``uniq``, ``python -m json.tool``, etc.) in order to
build up your own more complex scripts.

Currently available tools within ``ghtools``

==================   ======================================================
Command              Description
==================   ======================================================
gh-browse            Manually browse the GitHub API by URL
gh-list-members      List members of a GitHub organisation (may be removed)
gh-login             Login to GitHub, generating an OAuth login token
gh-migrate-project   Migrate an entire project between GitHub instances
gh-migrate-teams     Migrate organisation teams between GitHub instances
gh-org               Interact with organisations 
gh-repo              Interact with repositories
gh-status            Submit commit build status to GitHub
==================   ======================================================


Multiple instances
------------------

``ghtools`` is, in particular, designed for interacting with multiple GitHub
instances (i.e. github.com as well as your company's GitHub Enterprise
installation). You tell ``ghtools`` how to connect you non-github.com GitHub
instances using "nicknames" and environment variables. For example, here's how
to login to a GitHub instance nicknamed "foo", using a custom SSL cert
bundle::

    $ export GITHUB_FOO_API_ROOT=https://github.foo/api/v3
    $ export GITHUB_FOO_CA_BUNDLE=/usr/share/ssl/github_foo.crt
    $ eval `gh-login --scope repo foo`
    $ gh-repo foo:alphagov/ghtools get
    $ gh-org foo:alphagov members 

License
-------

``ghtools`` is released under the MIT license, a copy of which can be found
in ``LICENSE``.
