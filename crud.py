#!/usr/bin/env python

import requests
import json

## exceptions

## globals

# labels cannot begin with a number, else syntax error

#
# request success codes:
# use the numbers for directly comparing to a requests object's status_code
# use the longer form for exception messages
#
_200_="200"
_200_OK_="200 - API request succeeded"
OK = _200_ # for simple comparisons to str(requests.codes.ok)
_201_="201"
_201_SUCCEEDED_WITH_RESULTS_= \
    "201 - API request succeeded with results returned"
_202_="202"
_202_ACCEPTED_="202 - API request accepted"
ACCEPTED = _202_ # for simple comparisons to str(requests.codes.ok)
_204_="204"
_204_NO_CONTENT_="204 - API request succeeded but returned no content"
_206_="206"
_206_PARTIAL_CONTENT_="206 - API request OK but partial content returned"

SUCCEEDED=(
          _200_OK_,
          _201_SUCCEEDED_WITH_RESULTS_,
          _202_ACCEPTED_,
          _204_NO_CONTENT_,
          _206_PARTIAL_CONTENT_
          )

# for simple message processing
REQUEST_NOT_OK="API request is not OK"
REQUEST_NOT_ACCEPTED="API request is not ACCEPTED"

#
# request error codes:
# use the numbers for directly comparing to a requests object's status_code
# use the longer form for exception messages
#
_400_="400"
_400_REQUEST_INVALID_SYNTAX_="400 - API request syntax is malformed"
_401_="401"
_401_INVALID_CREDENTIALS_= \
    "401 - API request has missing or invalid credentials"
_403_="403"
_403_UNAUTHORIZED_="403 - API request is unauthorized"
_404_="404"
_404_RESOURCE_DOES_NOT_EXIST_="404 - API requested resource does not exist"
_409_="409"
_409_RESOURCE_CONFLICT_= \
    "409 - API requested resource is in a conflicted state"
_415_="415"
_415_UNSUPPORTED_BODY_FORMAT_= \
    "415 - API request body is in an unsupported format"
_500_="500"
_500_SERVER_REQUEST_FAILED_="500 - Server could not fulfill the API request"
_501_="501"
_501_SERVER_NO_FUNCTION_= \
    "501 - Server has not implemented the requested function"
_503_="503"
_503_SERVER_UNAVAILABLE_="503 - Server is unavailable"
_504_="504"
_504_SERVER_TIMEOUT_="504 - Server did not respond before request timed-out"

ERROR_MSGS={
           _400_ : _400_REQUEST_INVALID_SYNTAX_,
           _401_ : _401_INVALID_CREDENTIALS_,
           _403_ : _403_UNAUTHORIZED_,
           _404_ : _404_RESOURCE_DOES_NOT_EXIST_,
           _409_ : _409_RESOURCE_CONFLICT_,
           _415_ : _415_UNSUPPORTED_BODY_FORMAT_,
           _500_ : _500_SERVER_REQUEST_FAILED_,
           _501_ : _501_SERVER_NO_FUNCTION_,
           _503_ : _503_SERVER_UNAVAILABLE_,
           _504_ : _504_SERVER_TIMEOUT_
           }

class CrudError(Exception):

    def __init__(self, msg):
        super(CrudError, self).__init__(msg)

## end class CrudError

class Crud(object):

    def __init__(self):
        self.__results = {}

## end __init__

    @property
    def results(self):
        return self.__results

## end results getter

    def get(self, url, headers=None, body="", verify=False, timeout=5):
        resp = requests.request("GET",
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if resp.status_code in ERROR_MSGS:
            raise CrudError(
                "get: request failed: %s" %
                ERROR_MSGS[str(resp.status_code)]
                           ) 
        # if no content is returned
        if str(resp.status_code) == _204_:
            raise CrudError(
                "get: %s: %s" % (_204_NO_CONTENT_, str(resp.status_code))
                           )
        self.__results = json.loads(resp.text)
        return self.__results, str(resp.status_code)

## end get()

    def put(self, url, headers={}, body={}, verify=False, timeout=5):
        resp = requests.request("PUT",
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if resp.status_code in ERROR_MSGS:
            raise CrudError(
                "put: request failed: %s" %
                ERROR_MSGS[str(resp.status_code)]
                           ) 
        # if no content is returned
        if str(resp.status_code) == _204_:
            raise CrudError(
                "get: %s: %s" % (_204_NO_CONTENT_, str(resp.status_code))
                           )
        self.__results = json.loads(resp.text)
        return self.__results, str(resp.status_code)

## end put()

    def post(self, url, headers={}, body={}, verify=False, timeout=5):
        resp = requests.request("POST",
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if resp.status_code in ERROR_MSGS:
            raise CrudError(
                "post: request failed: %s" %
                ERROR_MSGS[str(resp.status_code)]
                           ) 
        # if no content is returned
        if str(resp.status_code) == _204_:
            raise CrudError(
                "get: %s: %s" % (_204_NO_CONTENT_, str(resp.status_code))
                           )
        self.__results = json.loads(resp.text)
        return self.__results, str(resp.status_code)

## end post()

    def delete(self, url, headers={}, body={}, verify=False, timeout=5):
        resp = requests.request("DELETE",
                                url,
                                headers=headers,
                                data=body,
                                verify=verify,
                                timeout=timeout)
        if resp.status_code in ERROR_MSGS:
            raise CrudError(
                "delete: request failed: %s" %
                ERROR_MSGS[str(resp.status_code)]
                           ) 
        # if no content is returned
        if str(resp.status_code) == _204_:
            raise CrudError(
                "get: %s: %s" % (_204_NO_CONTENT_, str(resp.status_code))
                           )
        self.__results = json.loads(resp.text)
        return self.__results, str(resp.status_code)

## end delete()

## end class Crud

## begin unit test

if __name__ == '__main__':

    from dnac import Dnac

    print "Crud:"
    print
    print "Setting up test..."
    print

    # target server + object handles login, auth token and headers
    d = Dnac()
    # target resource - returns a single switch from Dnac
    res = "/api/v1/network-device/a0116157-3a02-4b8d-ad89-45f45ecad5da"
    # target URL
    u = d.url + res
    # class under test
    c = Crud()

    print "  url =  " + u
    print "  hdrs = " + str(d.hdrs)
    print
    print "Getting (reading) a resource from a server..."
    print

    results, status = c.get(u, headers=d.hdrs)

    print "  status    = " + str(status)
    print "  results   = " + str(results)
    print "  c.results = " + str(c.results)
    print

    print "Testing Exceptions..."
    print

    def raiseCrudError(msg):
        raise CrudError(msg)

    errors = (REQUEST_NOT_OK,
              REQUEST_NOT_ACCEPTED,
              _204_NO_CONTENT_,
              _206_PARTIAL_CONTENT_,
              _400_REQUEST_INVALID_SYNTAX_,
              _401_INVALID_CREDENTIALS_,
              _403_UNAUTHORIZED_,
              _404_RESOURCE_DOES_NOT_EXIST_,
              _409_RESOURCE_CONFLICT_,
              _415_UNSUPPORTED_BODY_FORMAT_,
              _500_SERVER_REQUEST_FAILED_,
              _501_SERVER_NO_FUNCTION_,
              _503_SERVER_UNAVAILABLE_,
              _504_SERVER_TIMEOUT_)

    for error in errors:
        try:
            raiseCrudError(error)
        except CrudError, e:
            print "%s = %s" % (str(type(e)), str(e))

    print
    print "Crud unit test complete."

