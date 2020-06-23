# from .errorMessage import ErrorMessage
from base64 import b64encode

import requests
import terminusdb_client.woql_utils as utils

from .api_endpoint_const import APIEndpointConst
from .errors import APIError


class DispatchRequest:
    def __init__(self):
        pass

    @staticmethod
    def __get_call(url, headers, payload):
        url = utils.add_params_to_url(url, payload)

        return requests.get(url, headers=headers)

    @staticmethod
    def __post_call(url, headers, payload, file_dict=None):
        if file_dict:
            return requests.post(url, json=payload, headers=headers, files=file_dict)
        else:
            headers["content-type"] = "application/json"
            return requests.post(url, json=payload, headers=headers)

    @staticmethod
    def __delete_call(url, headers, payload):
        url = utils.add_params_to_url(url, payload)
        return requests.delete(url, headers=headers)

    @staticmethod
    def __autorization_header(basic_auth=None, remote_auth=None):
        headers = {}

        # if (payload and ('terminus:user_key' in  payload)):
        # utils.encodeURIComponent(payload['terminus:user_key'])}
        if basic_auth:
            headers["Authorization"] = "Basic %s" % b64encode(
                (basic_auth).encode("utf-8")
            ).decode("utf-8")
        if remote_auth and remote_auth["type"] == "jwt":
            headers["Authorization-Remote"] = "Bearer %s" % remote_auth["key"]
        elif remote_auth and remote_auth["type"] == "basic":
            rauthstr = remote_auth["user"] + ":" + remote_auth["key"]
            headers["Authorization-Remote"] = "Basic %s" % b64encode(
                (rauthstr).encode("utf-8")
            ).decode("utf-8")
        return headers

    # url, action, payload, basic_auth, jwt=null

    @classmethod
    def send_request_by_action(
        cls,
        url,
        action,
        payload=None,
        basic_auth=None,
        remote_auth=None,
        file_dict=None,
    ):
        # payload default as empty dict is against PEP
        # print("Sending to URL____________", url)
        # print("Send Request By Action_____________", action)
        if payload is None:
            payload = {}

        try:
            request_response = None
            headers = cls.__autorization_header(basic_auth, remote_auth)

            if action in [
                APIEndpointConst.GET_TRIPLES,
                APIEndpointConst.CONNECT,
                APIEndpointConst.CLASS_FRAME,
            ]:
                request_response = cls.__get_call(url, headers, payload)

            elif action in [
                APIEndpointConst.DELETE_DATABASE,
                APIEndpointConst.DELETE_GRAPH,
            ]:
                request_response = cls.__delete_call(url, headers, payload)

            elif action in [
                APIEndpointConst.WOQL_QUERY,
                APIEndpointConst.CREATE_DATABASE,
                APIEndpointConst.UPDATE_TRIPLES,
                APIEndpointConst.CREATE_GRAPH,
                APIEndpointConst.FETCH,
                APIEndpointConst.PULL,
                APIEndpointConst.PUSH,
                APIEndpointConst.REBASE,
                APIEndpointConst.BRANCH,
                APIEndpointConst.CLONE,
            ]:
                request_response = cls.__post_call(url, headers, payload, file_dict)

            if request_response.status_code == 200:
                return request_response.json()  # if not a json not it raises an error
            else:
                # Raise an exception if a request is unsuccessful
                message = "Api Error"

                if type(request_response.text) is str:
                    message = request_response.text

                raise (
                    APIError(
                        message,
                        url,
                        request_response.json(),
                        request_response.status_code,
                    )
                )

        # to be reviewed
        # the server in the response return always content-type application/json
        except ValueError:
            # if the response type is not a json
            # print("Value Error", err)
            return request_response.text

        """
        except Exception as err:
            print(type(err))
            print(err.args)

        except requests.exceptions.RequestException as err:
            print ("Request Error",err)
        except requests.exceptions.HTTPError as err:
            print ("Http Error:",err)
        except requests.exceptions.ConnectionError as err:
            print ("Error Connecting:",err)
        except requests.exceptions.Timeout as err:
            print ("Timeout Error:",err)
        """
