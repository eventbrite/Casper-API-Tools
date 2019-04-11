import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()
#print("JSS API Base URL: {}".format(jss_api_base_url))

def getAllPolicies(username, password):
	''' List all policies in JSS to screen '''
	#print(username)

	print "We're Refactored!  Getting All JAMF Policies..."
	reqStr = jss_api_base_url + '/policies'

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	baseXml = r.read()
	responseXml = etree.fromstring(baseXml)

	for policy in responseXml.findall('policy'):
		policyName = policy.find('name').text
		policyID = policy.find('id').text

		print 'Policy ID: ' + policyID + ',  ' + 'Policy Name: ' + policyName + '\n'
