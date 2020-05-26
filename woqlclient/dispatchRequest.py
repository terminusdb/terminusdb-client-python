# from .errorMessage import ErrorMessage
from base64 import b64encode

import requests

from .api_endpoint_const import APIEndpointConst
from .errors import APIError
from .utils import Utils


class DispatchRequest:
    def __init__(self):
        pass

    @staticmethod
    def __getCall(url, headers, payload):
        url = Utils.addParamsToUrl(url, payload)

        return requests.get(url, headers=headers)

    @staticmethod
    def __postCall(url, headers, payload, file_dict=None):
        if file_dict:
            return requests.post(url, json=payload, headers=headers, files=file_dict)
        else:
            headers["content-type"] = "application/json"
            return requests.post(url, json=payload, headers=headers)

    @staticmethod
    def __deleteCall(url, headers, payload):
        url = Utils.addParamsToUrl(url, payload)
        return requests.delete(url, headers=headers)

    @staticmethod
    def __autorizationHeader(key=None, jwt=None):
        headers = {}

        # if (payload and ('terminus:user_key' in  payload)):
        # Utils.encodeURIComponent(payload['terminus:user_key'])}
        if key:
            headers["Authorization"] = "Basic %s" % b64encode(
                (":" + key).encode("utf-8")
            ).decode("utf-8")
            if jwt:
                headers["HUB_AUTHORIZATION"] = "Bearer %s" % jwt
        # payload.pop('terminus:user_key')
        elif jwt:
            headers["Authorization"] = "Bearer %s" % jwt

        return headers

    # url, action, payload, basic_auth, jwt=null

    @classmethod
    def sendRequestByAction(
        cls, url, action, key, payload={}, file_dict=None, jwt=None
    ):
        print("Sending to URL____________", url)
        print("sendRequestByAction_____________", action)

        try:
            requestResponse = None
            headers = cls.__autorizationHeader(key, jwt)

            if action in [
                APIEndpointConst.CONNECT,
                APIEndpointConst.GET_SCHEMA,
                APIEndpointConst.CLASS_FRAME,
                APIEndpointConst.WOQL_SELECT,
                APIEndpointConst.GET_DOCUMENT,
            ]:
                requestResponse = cls.__getCall(url, headers, payload)

            elif action in [APIEndpointConst.DELETE_DATABASE, APIEndpointConst.DELETE_DOCUMENT]:
                requestResponse = cls.__deleteCall(url, headers, payload)

            elif action in [
                APIEndpointConst.CREATE_DATABASE,
                APIEndpointConst.UPDATE_SCHEMA,
                APIEndpointConst.CREATE_DOCUMENT,
                APIEndpointConst.WOQL_UPDATE,
            ]:
                requestResponse = cls.__postCall(url, headers, payload, file_dict)

            if requestResponse.status_code == 200:
                return requestResponse.json()  # if not a json not it raises an error
            else:
                # Raise an exception if a request is unsuccessful
                message = "Api Error"

                if type(requestResponse.text) is str:
                    message = requestResponse.text

                raise (
                    APIError(
                        message,
                        url,
                        requestResponse.json(),
                        requestResponse.status_code,
                    )
                )

        # to be reviewed
        # the server in the response return always content-type application/json
        except ValueError as err:
            # if the response type is not a json
            print("Value Error", err)
            return requestResponse.text

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
