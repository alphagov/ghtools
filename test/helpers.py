import os

from nose.tools import *
from mock import MagicMock, patch

from .requestmocker import RequestMockTestCase

HERE = os.path.dirname(__file__)

def fixture(name):
    return open(os.path.join(HERE, 'fixtures', name)).read()
