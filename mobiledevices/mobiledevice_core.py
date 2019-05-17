import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree
import urllib2

jss_api_base_url = jamfconfig.getJSS_API_URL()

def getMobileDevice(mobileDeviceName, username, password, detail):
	print("Running refactored getMobileDevice...")

	mobileDeviceName_normalized = urllib2.quote(mobileDeviceName)
	reqStr = jss_api_base_url + '/mobiledevices/match/' + mobileDeviceName_normalized
	#print reqStr
	#print detail

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	print 'All mobile devices with ' + mobileDeviceName + ' as part of the device information:\n'

	for mobile_device in responseXml.findall('mobile_device'):
		name = mobile_device.find('name').text
		sn = mobile_device.find('serial_number').text
		mac_addr = mobile_device.find('mac_address').text
		jssID = mobile_device.find('id').text

		if detail == 'yes':
			getMobileDeviceByID(jssID, username, password)
		else:
			print 'Mobile Device Name: ' + name
			print 'Serial Number: ' + sn
			print 'Mac Address: ' + str(mac_addr)
			print 'JSS Mobile Device ID: ' + jssID + '\n'

## Get single mobile device Id. If no results, return -1, if more than one result, return -2, if exactly one result, return mobile device id.
def getMobileDeviceId(mobileDeviceName, username, password):
	print("Running refactored getMobileDeviceByID...")
	mobileDeviceName_normalized = urllib2.quote(mobileDeviceName)
	reqStr = jss_api_base_url + '/mobiledevices/match/' + mobileDeviceName_normalized

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return -1

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	response_size = responseXml.find('size').text

	if response_size == '0':
		#print 'Mobile Device not found, please search again.'
		return -1
	elif response_size == '1':
		return responseXml.find('mobile_device/id').text
	else:
		#print 'Too many results, narrow your search paramaters.'
		return -2

def getMobileDeviceByID(mobileID, username, password):
	print "Getting mobile device with JSS ID " + mobileID + "..."
	reqStr = jss_api_base_url + '/mobiledevices/id/' + mobileID

	#print reqStr

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code

		#print 'Response Code: ' + str(responseCode)

		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)

		#print responseXml.tag

		general = responseXml.find('general')
		jssID = general.find('id').text
		name = general.find('name').text
		model = general.find('model').text
		last_inventory_update = general.find('last_inventory_update').text
		asset_tag = general.find('asset_tag').text
		os_version = general.find('os_version').text
		sn = general.find('serial_number').text
		mac_addr = general.find('wifi_mac_address').text
		ip_addr = general.find('ip_address').text
		managed = general.find('managed').text
		supervised = general.find('supervised').text

		print '\nGENERAL INFORMATION:'
		print 'JSS Mobile Device ID: ' + jssID
		print 'Mobile Name: ' + name
		print 'Model: ' + model
		print 'Last Inventory Update: ' + last_inventory_update
		print 'Asset Number: ' + str(asset_tag)
		print 'OS Version: ' + os_version
		print 'Serial Number: ' + sn
		print 'Mac Address: ' + mac_addr
		print 'IP Address: ' + ip_addr
		print 'Managed: ' + managed
		print 'Supervised: ' + supervised


		assigned_user = responseXml.find('location/username').text
		real_name = responseXml.find('location/real_name').text
		email_address = responseXml.find('location/email_address').text
		position = responseXml.find('location/position').text
		phone = responseXml.find('location/phone').text
		department = responseXml.find('location/department').text
		building = responseXml.find('location/building').text
		room = responseXml.find('location/room').text

		print '\nUSER AND LOCATION:'
		print 'Username: ' + str(assigned_user)
		print 'Real Name: ' + str(real_name)
		print 'Email: ' + str(email_address)
		print 'Position: ' + str(position)
		print 'Phone: ' + str(phone)
		print 'Department: ' + str(department)
		print 'Building: ' + str(building)
		print 'Room: ' + str(room)

		mobile_device_groups = responseXml.find('mobile_device_groups')

		groups = []
		for group in mobile_device_groups.findall('mobile_device_group'):
			groupId = group.find('id').text
			groupName = group.find('name').text
			groupPair = str(groupId) + ': ' + str(groupName)
			groups += [ groupPair ]
			#print groupName
		print '\nMOBILE DEVICE GROUPS: '
		print '\n'.join (sorted (groups))

		print '\n'
		#print prettify(responseXml)

		#print etree.tostring(responseXml)
	else:
		print 'Failed to find mobile device with JSS ID ' + mobileID