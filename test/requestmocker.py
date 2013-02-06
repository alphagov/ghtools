from collections import namedtuple
from httplib import responses

from mock import patch

from requests import Response, Session
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers

class MockConnection(object):
    pass


class MockRawResponse(object):
    pass


class SessionMaker(object):
    """

    An object that stores a set of mocked-out (method, url) pairs, and is able
    to make :class:`requests.Session` objects that respond with the mocked
    values when requests are made against them.

    """

    def __init__(self):
        self._responses = {}

    def __call__(self, *args, **kwargs):
        sess = Session(*args, **kwargs)
        sess.send = self._make_send_func_for_session(sess)
        return sess

    def register_response(self, method, url, *args, **kwargs):
        """Mock a response for the passed (method, url) pair"""
        self._responses[(method.upper(), url)] = (args, kwargs)

    def unregister_response(self, method, url):
        """Unmock a response for the passed (method, url) pair"""
        self._responses.pop((method.upper(), url))

    def response_for(self, method, url):
        """Return any mocked response for the passed (method, url) pair"""
        return self._responses.get((method.upper(), url))

    def _make_send_func_for_session(self, session):
        """
        Make a function to replace :method:`requests.Session.send` for the
        specified session
        """
        session._original_send = session.send
        def send(request, **kwargs):
            response = self.response_for(request.method, request.url)
            if response is not None:
                build_response_args, build_response_kwargs = response
                return build_response(request, *build_response_args, **build_response_kwargs)
            # If no mocked response, fall back to making a request as usual
            else:
                return session._original_send(request, **kwargs)
        return send


class RequestMockTestCase(object):

    def setup(self):
        if not hasattr(self, 'session_to_patch'):
            raise RuntimeError("You should set self.session_to_patch before calling "
                               "super(..., self).setup() in subclasses of RequestMockTestCase")

        self._session_patcher = patch(self.session_to_patch, new_callable=SessionMaker)
        self._session_maker = self._session_patcher.start()

    def teardown(self):
        self._session_patcher.stop()

    # Pass response registration/unregistration through to the relevant
    # RequestMocker instance
    def register_response(self, *args, **kwargs):
        return self._session_maker.register_response(*args, **kwargs)

    def unregister_response(self, *args, **kwargs):
        return self._session_maker.unregister_response(*args, **kwargs)


def build_response(request,
                   status_code=200,
                   headers={},
                   content='(none)'):
    """
    Build a :class:`requests.Response` object on the basis of the passed
    parameters.
    """

    response = Response()

    response.status_code = status_code
    response.reason = responses[status_code]
    response.headers = CaseInsensitiveDict(headers)
    # Pretend that we've already read from the socket
    response._content = content

    response.encoding = get_encoding_from_headers(response.headers)
    response.url = request.url
    response.raw = MockRawResponse()

    # Give the Response some context.
    response.request = request
    response.connection = MockConnection()

    return response


