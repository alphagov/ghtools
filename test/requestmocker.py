import json

from mock import MagicMock, patch

from requests import Response
from requests.structures import CaseInsensitiveDict


class RequestMockTestCase(object):

    def setup(self):
        if not hasattr(self, 'session_to_patch'):
            raise RuntimeError("You should set self.session_to_patch before calling super(..., self).setup() in subclasses of RequestMockTestCase")

        self._urls = {}

        self._sess_patcher = patch(self.session_to_patch)
        sess_mock = self._sess_patcher.start()
        self._resp_mock = sess_mock.return_value.request

        def _match(method, url, *args, **kwargs):
            default = ((), {})
            mr_args, mr_kwargs = self._urls.get((method, url), default)
            return self._mock_response(*mr_args, **mr_kwargs)

        self._resp_mock.side_effect = _match

    def _mock_response(self, status_code=404, headers={}, content='PAGE_NOT_FOUND'):
        r = MagicMock(Response())
        r.status_code = status_code
        r.headers = CaseInsensitiveDict(headers if headers is not None else {})
        r.content = content
        r.json.side_effect = lambda: json.loads(content)
        r.ok = status_code < 400
        return r

    def teardown(self):
        self._sess_patcher.stop()

    def register_response(self, method, url, *args, **kwargs):
        self._urls[(method, url)] = (args, kwargs)

    def unregister_response(self, method, url):
        self._urls.pop((method, url))
