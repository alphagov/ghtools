Hacking on ghtools
==================

Prerequisites
-------------

You'll need Python_ and pip_ to install a development environment for
``ghtools``. On a Mac::

    $ brew install python
    $ echo 'export PATH="/usr/local/share/python:$PATH"' >> ~/.bashrc
    $ exec $SHELL

You should then install virtualenv_, virtualenvwrapper_, and tox_::

    $ pip install virtualenv virtualenvwrapper tox
    $ echo '. /usr/local/share/python/virtualenvwrapper_lazy.sh' >> ~/.bashrc
    $ exec $SHELL

.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
.. _tox: http://tox.readthedocs.org/

You should now be able to create a virtualenv in which to work on ``ghtools``
(this means that ``ghtools`` and its dependencies aren't installed into your
system Python)::

    $ mkvirtualenv ghtools

You can "exit" the virtualenv by typing::

    (ghtools)$ deactivate

Development workflow
--------------------

When you want to work in your ``ghtools`` virtualenv, simply type::

    $ workon ghtools

To install ``ghtools`` into your virtualenv, now run the following from the
repository root::

    $ pip install -e .
    ...
    Installing collected packages: ghtools
    ...
    Installed /Volumes/gds/govuk/ghtools
    Successfully installed ghtools
    Cleaning up...

You should now be able to run the ``ghtools`` executables which will point
directly at your checked out source code::

    $ eval `gh-login`

Testing
-------

Tests are run using tox_, a multi-environment virtualenv_-based test runner::

    $ tox
    GLOB sdist-make: /Volumes/gds/govuk/ghtools/setup.py
    py27 sdist-reinst: /Volumes/gds/govuk/ghtools/.tox/dist/ghtools-0.9.0.zip
    py27 runtests: commands[0]
    .......................................................
    ----------------------------------------------------------------------
    Ran 55 tests in 0.288s

    OK
    pypy sdist-reinst: /Volumes/gds/govuk/ghtools/.tox/dist/ghtools-0.9.0.zip
    pypy runtests: commands[0]
    .......................................................
    ----------------------------------------------------------------------
    Ran 55 tests in 0.601s

    OK
    ________________________________ summary ________________________________
      py27: commands succeeded
      pypy: commands succeeded
      congratulations :)

If you don't have PyPy_ installed, then you can ask tox to only run tests for
one version of Python::

   $ tox -e py27

.. _PyPy: http://pypy.org/

Gotchas
-------

If you bump the version of ``ghtools``, you will need to reinstall the package
into your virtualenv, or your executables will stop working::

   $ gh-repo -h
   Traceback (most recent call last):
     File ".../ghtools/bin/gh-repo", line 5, in <module>
       from pkg_resources import load_entry_point
     File ".../ghtools/lib/python2.7/site-packages/distribute-0.6.27-py2.7.egg/pkg_resources.py", line 2739, in <module>
       parse_requirements(__requires__), Environment()
     File ".../ghtools/lib/python2.7/site-packages/distribute-0.6.27-py2.7.egg/pkg_resources.py", line 588, in resolve
       raise DistributionNotFound(req)
   pkg_resources.DistributionNotFound: ghtools==0.1.0
   $ pip install -e .
   ...
   $ gh-repo -h
   usage: gh-repo [-h] repo {delete,get} ...

If you update ``ghtools`` requirements (``install_requires`` in setup.py) you
will need to tell tox to recreate the test environments::

   $ tox -r -e py27
