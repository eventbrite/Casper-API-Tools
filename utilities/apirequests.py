import urllib2
import requests
from requests.auth import HTTPBasicAuth
import base64

def sendAPIRequest(reqStr, username, password, method, XML=''):

	errorMsg_401 = 'Authentication failed. Check your JSS credentials.'
	errorMsg_404 = 'The JSS could not find the resource you were requesting. Check the URL to the resource you are using.'

	request = urllib2.Request(reqStr)
	request.add_header('Authorization', 'Basic ' + base64.b64encode(username + ':' + password))

	if method == "GET":
		# GET
		try:
			request.add_header('Accept', 'application/xml')
			response = urllib2.urlopen(request)
			return response
		except urllib2.HTTPError, e:
			print 'Request failed with error code - %s.' % e.code

			if e.code == 401:
				print errorMsg_401
			elif e.code == 404:
				print errorMsg_404

			return -1
	elif method == "POST":
		# POST
		request.add_header('Content-Type', 'text/xml')
		request.get_method = lambda: 'POST'
		response = urllib2.urlopen(request, XML)
	elif method == "PUT":
		# PUT
		request.add_header('Content-Type', 'text/xml')
		request.get_method = lambda: 'PUT'
		try:
			response = urllib2.urlopen(request, XML)
			return response
		except urllib2.HTTPError, e:
			print 'Request failed with error code - %s.' % e.code

			if e.code == 401:
				print errorMsg_401
			elif e.code == 404:
				print errorMsg_404

			return -1
	elif method == "DELETE":
		# DELETE
		request.get_method = lambda: 'DELETE'
		try:
			response = urllib2.urlopen(request)
			return response
		except urllib2.HTTPError, e:
			print 'Request failed with error code - %s.' % e.code

			if e.code == 401:
				print errorMsg_401
			elif e.code == 404:
				print errorMsg_404

			return -1
	else:
		print 'Unknown method.'
		return -1

def sendAPIGetRequest(reqStr, username, password, method):
    ''' simple GET API request to JSS API using requests library'''

    errorMsg_401 = 'Authentication failed. Check your JSS credentials.'
    errorMsg_404 = 'The JSS could not find the resource you were requesting. Check the URL to the resource you are using.'

    response = requests.get(
        reqStr, headers={'Accept':'application/json'},
        auth=HTTPBasicAuth(username, password)
        )

    if response:
        print('Successful Response from JSS API')
        return response.json()

    elif response.status_code == 401:
        print(errorMsg_401)

    elif response.status_code == 404:
        print(errorMsg_404)
