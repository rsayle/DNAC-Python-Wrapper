
import requests
import json

#
# request success codes:
# use the numbers for directly comparing to a requests object's status_code
# use the longer form for exception messages
#
_200_ = 200
_200_OK_ = '200 - API request succeeded'
OK = _200_  # for simple comparisons to str(requests.codes.ok)
_201_ = 201
_201_SUCCEEDED_WITH_RESULTS_ = '201 - API request succeeded with results returned'
_202_ = 202
_202_ACCEPTED_ = '202 - API request accepted'
ACCEPTED = _202_  # for simple comparisons to str(requests.codes.ok)
_204_ = 204
_204_NO_CONTENT_ = '204 - API request succeeded but returned no content'
_206_ = 206
_206_PARTIAL_CONTENT_ = '206 - API request OK but partial content returned'

SUCCEEDED = (
             _200_OK_,
             _201_SUCCEEDED_WITH_RESULTS_,
             _202_ACCEPTED_,
             _204_NO_CONTENT_,
             _206_PARTIAL_CONTENT_
            )

# for simple message processing
REQUEST_NOT_OK = 'API request is not OK'
REQUEST_NOT_ACCEPTED = 'API request is not ACCEPTED'

#
# request error codes:
# use the numbers for directly comparing to a requests object's status_code
# use the longer form for exception messages
#
_400_ = 400
_400_REQUEST_INVALID_SYNTAX_ = '400 - API request syntax is malformed'
_401_ = 401
_401_INVALID_CREDENTIALS_ = '401 - API request has missing or invalid credentials'
_403_ = 403
_403_UNAUTHORIZED_ = '403 - API request is unauthorized'
_404_ = 404
_404_RESOURCE_DOES_NOT_EXIST_ = '404 - API requested resource does not exist'
_409_ = 409
_409_RESOURCE_CONFLICT_ = '409 - API requested resource is in a conflicted state'
_415_ = 415
_415_UNSUPPORTED_BODY_FORMAT_ = '415 - API request body is in an unsupported format'
_417_ = 417
_417_EXPECTATION_FAILED_ = '417 - The server cannot meet the requirements of the Expect request-header field'
_500_ = 500
_500_SERVER_REQUEST_FAILED_ = '500 - Server could not fulfill the API request'
_501_ = 501
_501_SERVER_NO_FUNCTION_ = '501 - Server has not implemented the requested function'
_503_ = 503
_503_SERVER_UNAVAILABLE_ = '503 - Server is unavailable'
_504_ = 504
_504_SERVER_TIMEOUT_ = '504 - Server did not respond before request timed-out'

ERROR_MSGS = {
              _400_: _400_REQUEST_INVALID_SYNTAX_,
              _401_: _401_INVALID_CREDENTIALS_,
              _403_: _403_UNAUTHORIZED_,
              _404_: _404_RESOURCE_DOES_NOT_EXIST_,
              _409_: _409_RESOURCE_CONFLICT_,
              _415_: _415_UNSUPPORTED_BODY_FORMAT_,
              _417_: _417_EXPECTATION_FAILED_,
              _500_: _500_SERVER_REQUEST_FAILED_,
              _501_: _501_SERVER_NO_FUNCTION_,
              _503_: _503_SERVER_UNAVAILABLE_,
              _504_: _504_SERVER_TIMEOUT_
             }


class Crud(object):
    """
    Class Crud handles REST API calls (get, put, post and delete) to a
    server.  It converts the JSON formatted response it receives into
    appropriate python data types and then stores it in its __results
    attribute.

    Attributes:
        results: The results returned by a CRUD API call.
            type: dict
            default: none
            scope: protected

    Usage:
        rest_api = Crud()
    """

    def __init__(self):
        """
        Crud's __init__ method sets up its results attribute as an empty dictionary and then returns the newly created
        Crud object.
        """
        self.__results = {}

    # end __init__

    @property
    def results(self):
        """
        Crud's results get method returns the value of its __results attribute, which contains the response from the
        RESTful server.
        :return: dict
        """
        return self.__results

    # end results getter

    def get(self, url, headers=None, body="", verify=False, timeout=5, is_json=True):
        """
        Crud's get method performs a GET API call, a read request, to a server.  It stores the results and also returns
        them to the user along with the request's status code.
        :param url: The path to the server's API resource.
                type: str
                default: none
                required: yes
        :param headers: headers: The headers for placing an API call.
                type: dict
                default: none
                required: yes, as a keyword argument
        :param body: Any data elements required for the API call.
                type: str
                default: none
                required: no
        :param verify: A flag indicating if the server's certificate should be authenticated.
                type: bool
                default: False
                required: no
        :param timeout: Time in seconds to wait for the server's response before abandoning the API call.
                type: int
                default: 5
                required: no
        :param is_json: A flag indicating if the response is given in JSON format.
                type = bool
                default: False
                required: no
        :return: dict, str
        """
        if headers is None:
            headers = {}
        resp = requests.request('GET',
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if bool(resp) and is_json is True:  # resp is not empty and is json formatted
            self.__results = json.loads(resp.text)
        elif bool(resp) and is_json is False:  # resp is not empty and is not json formatted
            self.__results = resp.text
        return self.__results, resp.status_code

    # end get()

    def put(self, url, headers=None, body="", verify=False, timeout=5):
        """
        Crud's put method performs a PUT API call, an update request, to a server.  It stores the results and also
        returns them to the user along with the request's status code.
        :param url: he path to the server's API resource.
                type: str
                default: none
                required: yes
        :param headers: The headers for placing an API call.
                type: dict
                default: none
                required: yes, as a keyword argument
        :param body: Any data elements required for the API call.
                type: str
                default: none
                required: no
        :param verify: A flag indicating if the server's certificate should be authenticated.
                type: bool
                default: False
                required: no
        :param timeout: Time in seconds to wait for the server's response before abandoning the API call.
                type: int
                default: 5
                required: no
        :return: dict, str
        """
        if headers is None:
            headers = {}
        resp = requests.request('PUT',
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if bool(resp):
            self.__results = json.loads(resp.text)
        return self.__results, resp.status_code

    # end put()

    def post(self, url, headers=None, body="", verify=False, timeout=5):
        """
        Crud's post method performs a POST API call, a create request, to a server.  It stores the results and also
        returns them to the user along with the request's status code.
        :param url: he path to the server's API resource.
                type: str
                default: none
                required: yes
        :param headers: The headers for placing an API call.
                type: dict
                default: none
                required: yes, as a keyword argument
        :param body: Any data elements required for the API call.
                type: str
                default: none
                required: no
        :param verify: A flag indicating if the server's certificate should be authenticated.
                type: bool
                default: False
                required: no
        :param timeout: Time in seconds to wait for the server's response before abandoning the API call.
                type: int
                default: 5
                required: no
        :return: dict, str
        """
        if headers is None:
            headers = {}
        resp = requests.request('POST',
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if bool(resp):
            self.__results = json.loads(resp.text)
        return self.__results, resp.status_code

    # end post()

    def delete(self, url, headers=None, body="", verify=False, timeout=5):
        """
        Crud's delete method performs a DELETE API call, a delete request, to a server.  It stores the results and also
        returns them to the user along with the request's status code.
        :param url: he path to the server's API resource.
                type: str
                default: none
                required: yes
        :param headers: The headers for placing an API call.
                type: dict
                default: none
                required: yes, as a keyword argument
        :param body: Any data elements required for the API call.
                type: str
                default: none
                required: no
        :param verify: A flag indicating if the server's certificate should be authenticated.
                type: bool
                default: False
                required: no
        :param timeout: Time in seconds to wait for the server's response before abandoning the API call.
                type: int
                default: 5
                required: no
        """
        if headers is None:
            headers = {}
        resp = requests.request('DELETE',
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if bool(resp):
            self.__results = json.loads(resp.text)
        return self.__results, resp.status_code

    # end delete()

# end class Crud

