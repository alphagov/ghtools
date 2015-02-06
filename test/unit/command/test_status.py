from mock import patch
from ghtools.command.status import status, parser


class TestRepo(object):

    def setup(self):
        self.patcher = patch('ghtools.command.status.Repo')
        self.mock_repo = self.patcher.start()
        self.mock_repo.return_value.set_build_status.return_value.json.return_value = {}

    def teardown(self):
        self.patcher.stop()

    def test_status(self):
        args = parser.parse_args([
            'alphagov/foobar',
            'mybranch',
            'pending',
            '--description', 'Running on Jenkins',
            '--url', 'http://ci.alphagov.co.uk/foo',
            '--context', 'CI'
        ])
        status(args)
        self.mock_repo.assert_called_with('alphagov/foobar')
        self.mock_repo.return_value.set_build_status.assert_called_with(
            'mybranch',
            {
                'state': 'pending',
                'target_url': 'http://ci.alphagov.co.uk/foo',
                'description': 'Running on Jenkins',
                'context': 'CI'
            }
        )
