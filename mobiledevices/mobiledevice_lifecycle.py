import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree

import mobiledevice_core

jss_api_base_url = jamfconfig.getJSS_API_URL()

def deleteMobileDeviceByID(mobile_id, username, password):

	mobiledevice_core.getMobileDeviceByID(mobile_id, username, password)

	sure = raw_input('Are you sure you want to delete the mobile device above from the JSS? (y/n): ')

	if sure == 'y':
		print "Deleting mobile device " + mobile_id + "..."

		delStr = jss_api_base_url + '/mobiledevices/id/' + mobile_id
		#print delStr
		response = apirequests.sendAPIRequest(delStr, username, password, 'DELETE')

		if response == -1:
			print 'Failed to delete mobile device. See errors above.'
		else:
			print 'Successfully deleted mobile device ' + mobile_id

	else:
		print 'Aborting request to delete mobile device ' + mobile_id

		## Uncomment this part to see the xml response
		#xmlstring = response.read()
		#xml = etree.fromstring(xmlstring)
		#print prettify(xml)

		#responseCode = str(response.code)
		#print 'Response Code: ' + responseCode