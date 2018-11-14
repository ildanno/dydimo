#!/usr/bin/env python
# coding=utf-8

import sys
import oas3
import requests

# program arguments
filename = sys.argv[1]
baseurl = sys.argv[2]

specification = oas3.Spec.from_file(filename)  # type: oas3.Spec


class ExpectedResponse:
    contentType = ''
    responseCode = ''


class TestRequest:
    method = 'GET'
    path = ''
    contentType = ''
    responseCode = ''
    parameters = []
    expectedResponse = ExpectedResponse()


def build_request(method, path, responseCode, contentType, example):
    """

    :type method: str
    :type path: str
    :type example: dict
    """
    request = TestRequest()
    request.method = method.upper()
    request.path = path

    request.expectedResponse.contentType = contentType
    request.expectedResponse.responseCode = responseCode

    return request


paths = specification.paths

testRequests = []
for path in paths:
    operations = paths[path]
    for method in operations:  # type: str
        operation = operations[method]
        responses = operation['responses']
        for responseCode in responses:
            response = responses[responseCode]

            if 'content' not in response.keys():
                continue

            contentTypes = response['content']

            for contentType in contentTypes:
                responseExamples = contentTypes[contentType]['examples']

                for responseExampleName in responseExamples:
                    testRequests.append(build_request(method, path, responseCode, contentType, responseExamples[responseExampleName]))


for testRequest in testRequests:
    expected = testRequest.expectedResponse

    print ('Request:', testRequest.method, testRequest.path)
    print ('Expected Response: ' + expected.responseCode + ' (' + expected.contentType + ')')

    response = requests.request(testRequest.method, baseurl + testRequest.path)

    if 'Content-Type' in response.headers.keys():
        responseContentType = response.headers['Content-Type']
    else:
        responseContentType = ''

    problems = []
    if str(expected.responseCode) != str(response.status_code):
        problems.append('Actual Response Code ' + str(response.status_code) + ' differs from expected ' + str(expected.responseCode))

    if expected.contentType != responseContentType:
        problems.append('Actual Content Type ' + responseContentType + ' differs from expected ' + expected.contentType)

    if len(problems) == 0:
        print ("Status: OK")
    else:
        for problem in problems:
            print (problem)
