from dispatchRequest import DispatchRequest
import const
import pytest
import sys
sys.path.append('woqlclient')

#from pytest import mocker


# class dispatchRequestTests:


def mocked_requests_get(*args, **kwargs):

    class MockResponse:

        def _mock_response(
                self,
                status=200,
                content="CONTENT",
                json_data=None,
                raise_for_status=None):
            """
            since we typically test a bunch of different
            requests calls for a service, we are going to do
            a lot of mock responses, so its usually a good idea
            to have a helper function that builds these things
            """
            mock_resp = mocker.Mock()
            # mock raise_for_status call w/optional error
            mock_resp.raise_for_status = mocker.Mock()
            if raise_for_status:
                mock_resp.raise_for_status.side_effect = raise_for_status
            # set status code and content
            mock_resp.status_code = status
            mock_resp.content = content
            # add json data if provided

            with open('tests/capabilitiesResponse.json') as json_file:
                json_data = json.load(json_file)
                mock_resp.json = mocker.Mock(return_value=json_data)

                return mock_resp

    mockResp = MockResponse()
    if args[0] == 'http://localhost:6363/':
        return mockResp._mock_response()
        # elif args[0] == 'http://someotherurl.com/anothertest.json':
            # return MockResponse({"key2": "value2"}, 200)

    return mockResp._mock_response(200)

# Our test case class
# class dispatchRequestTests(mocker):

    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.


def test_connectCall(mocker):
    # Assert requests.get calls
    #assert (1 == 2) == True
    with mocker.patch('dispatchRequest.requests.get', side_effect=mocked_requests_get):
        dispatch = DispatchRequest()
        payload = {'terminus:user_key': "mykey"}
        json_data = dispatch.sendRequestByAction(
            'http://localhost:6363/', const.CONNECT, payload)


"""
    self.assertEqual(json_data, {"key1": "value1"})
    json_data = mgc.fetch_json('http://someotherurl.com/anothertest.json')
    self.assertEqual(json_data, {"key2": "value2"})
    json_data = mgc.fetch_json('http://nonexistenturl.com/cantfindme.json')
    self.assertIsNone(json_data)

    # We can even assert that our mocked method was called with the right parameters
    self.assertIn(mock.call('http://someurl.com/test.json'), mock_get.call_args_list)
    self.assertIn(mock.call('http://someotherurl.com/anothertest.json'), mock_get.call_args_list)

    self.assertEqual(len(mock_get.call_args_list), 3)
"""
