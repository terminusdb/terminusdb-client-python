# from .errorMessage import ErrorMessage
import json
import warnings
from base64 import b64encode

import requests
import terminusdb_client.woql_utils as utils
from urllib3.exceptions import InsecureRequestWarning

from .api_endpoint_const import APIEndpointConst
from .errors import APIError


def _verify_check(url, insecure=False):
    if url[:17] == "https://127.0.0.1" or url[:7] == "http://" or insecure:
        return False
    else:
        return True


class DispatchRequest:
    def __init__(self):
        pass

    @staticmethod
    def __get_call(url, headers, payload, insecure=False):
        url = utils.add_params_to_url(url, payload)
        if not _verify_check(url, insecure):
            warnings.simplefilter("ignore", InsecureRequestWarning)
        result = requests.get(url, headers=headers, verify=_verify_check(url, insecure))
        warnings.resetwarnings()
        return result

    @staticmethod
    def __post_call(url, headers, payload, file_dict=None, insecure=False):
        if not _verify_check(url, insecure):
            warnings.simplefilter("ignore", InsecureRequestWarning)
        if file_dict:
            file_dict["payload"] = (
                "payload",
                json.dumps(payload),
                "application/json",
            )

            result = requests.post(
                url,
                headers=headers,
                files=file_dict,
                verify=_verify_check(url, insecure),
            )
            # Close the files although request should do this :(
            for key in file_dict:
                (_, stream, _) = file_dict[key]
                if type(stream) != str:
                    stream.close()
        else:
            headers["content-type"] = "application/json"
            result = requests.post(
                url, json=payload, headers=headers, verify=_verify_check(url, insecure)
            )
        warnings.resetwarnings()
        return result

    @staticmethod
    def __put_call(url, headers, payload, file_dict=None, insecure=None):
        if not _verify_check(url):
            warnings.simplefilter("ignore", InsecureRequestWarning)
        if file_dict:
            file_dict["payload"] = (
                "payload",
                json.dumps(payload),
                "application/json",
            )

            result = requests.put(
                url, headers=headers, files=file_dict, verify=_verify_check(url),
            )
            # Close the files although request should do this :(
            for key in file_dict:
                (_, stream, _) = file_dict[key]
                if type(stream) != str:
                    stream.close()
        else:
            headers["content-type"] = "application/json"
            result = requests.put(
                url, json=payload, headers=headers, verify=_verify_check(url, insecure)
            )
        warnings.resetwarnings()
        return result

    @staticmethod
    def __delete_call(url, headers, payload, insecure=False):
        url = utils.add_params_to_url(url, payload)
        if not _verify_check(url, insecure):
            warnings.simplefilter("ignore", InsecureRequestWarning)
        result = requests.delete(
            url, headers=headers, verify=_verify_check(url, insecure)
        )
        warnings.resetwarnings()
        return result

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
        insecure=False,
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
                APIEndpointConst.GET_CSV,
                APIEndpointConst.CONNECT,
                APIEndpointConst.CLASS_FRAME,
            ]:
                request_response = cls.__get_call(
                    url, headers, payload, insecure=insecure
                )

            elif action in [
                APIEndpointConst.DELETE_DATABASE,
                APIEndpointConst.DELETE_GRAPH,
            ]:
                request_response = cls.__delete_call(
                    url, headers, payload, insecure=insecure
                )

            elif action in [
                APIEndpointConst.WOQL_QUERY,
                APIEndpointConst.CREATE_DATABASE,
                APIEndpointConst.UPDATE_TRIPLES,
                APIEndpointConst.UPDATE_CSV,
                APIEndpointConst.CREATE_GRAPH,
                APIEndpointConst.FETCH,
                APIEndpointConst.PULL,
                APIEndpointConst.PUSH,
                APIEndpointConst.REBASE,
                APIEndpointConst.BRANCH,
                APIEndpointConst.CLONE,
                APIEndpointConst.RESET,
                APIEndpointConst.OPTIMIZE,
                APIEndpointConst.SQUASH,
            ]:
                request_response = cls.__post_call(
                    url, headers, payload, file_dict, insecure=insecure
                )

            elif action in [
                APIEndpointConst.INSERT_TRIPLES,
                APIEndpointConst.INSERT_CSV,
            ]:

                request_response = cls.__put_call(
                    url, headers, payload, file_dict, insecure=insecure
                )

            if request_response.status_code == 200:
                # print("hellow ")
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
            return request_response

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
