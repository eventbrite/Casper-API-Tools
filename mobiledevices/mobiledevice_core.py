import sys
sys.path.append('..')
import csv
from csv import writer, DictWriter
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree
import urllib2

jss_api_base_url = jamfconfig.getJSS_API_URL()

def findMobileDeviceId(searchString, username, password):
	#print 'Searching for mobile device with string ' + searchString
	print "Running refactored findMobileDeviceId...\n"
	searchString_normalized = urllib2.quote(searchString)

	reqStr = jss_api_base_url + '/mobiledevices/match/' + searchString_normalized
	#print reqStr
	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		responseCode = r.code
		baseXml = r.read()
		responseXml = etree.fromstring(baseXml)
		#print prettify(responseXml)
		#return

		#mobiledevicemembers = responseXml.find('mobile_devices')
		#print mobiledevicemembers
		#return
		result_size = responseXml.find('size').text
		#print 'hello' + str(result_size)

		if result_size == '0':
			print 'No matches found.'
			return -1
		elif result_size == '1':
			#print 'Single match found'
			mobile_device_id = responseXml.find('mobile_device/id').text
			print mobile_device_id
			return mobile_device_id
			#print prettify(responseXml)
		else:
			print 'Multiple matches found, please narrow your search.'
			return -1
	else:
		print 'Error'


def getMobileDevice(mobileDeviceName, username, password, detail):
	print "Running refactored getMobileDevice...\n"

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
	print "Running refactored getMobileDeviceByID...\n"
	try:
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
	except KeyError as error:
		print 'Problem parsing device name. Possibly an invalid character'
		print error

def getMobileDeviceByID(mobileID, username, password):
	print "Running refactored getMobileDeviceByID...\n"
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


def getMobileDevicesCSV(devicesCSV, username, password):
	print "Running refactored getMobileDevicesCSV...\n"
	# CSV file with one column, search string

	devicesDict = {}

	with open (devicesCSV, 'rU') as csvfile:
		devicesreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		# Skip the header row
		next(devicesreader, None)

		for row in devicesreader:
			mobileSearch = row[0].replace('"', '').strip()
			## for each search string, retrieve the device and add to devicesDict with device-name as the key, and serial, asset, and jss-id as a list
			deviceInfo = getMobileDeviceInfo(mobileSearch, username, password)
			#print deviceInfo
			## check to make sure device exists
			if deviceInfo == -1:
				print 'Device ' + mobileSearch + ' not found, skipping...'
				#   deviceInfo = {}
				#   deviceInfo[]
			else:
				devicesDict.update(deviceInfo)

	# print devicesDict

	return devicesDict

def printMobileDevicesCSV(devicesCSV, username, password):
	print "Running refactored printMobileDevicesCSV...\n"
	devicesDict = getMobileDevicesCSV(devicesCSV, username, password)

	if len(devicesDict) == 0:
		print 'No devices found...'
		return -1

	print '\nDevice Name\tSerial Number\tAsset\tJSS ID'
	print '===========\t=============\t=====\t======'
	for (device, info) in devicesDict.items():
		# print info
		try:
			print "%s\t%s" % (device, '\t'.join(info))
		except TypeError as error:
			print device + ' has an empty field which can\'t be displayed: ' + str(error)

	return devicesDict


def getMobileDeviceInfo(mobileSearch, username, password):
	print "Running refactored getMobileDeviceInfo...\n"

	## Get Device name for assetTag
	mobileDeviceName_normalized = urllib2.quote(mobileSearch)
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
		device_name = responseXml.find('mobile_device/name').text
		device_id = responseXml.find('mobile_device/id').text
		device_serial = responseXml.find('mobile_device/serial_number').text
	else:
		#print 'Too many results, narrow your search paramaters.'
		return -2

	device_asset_tag = getMobileDeviceAssetTag(device_id, username, password)

	# Build a dict keyed off the device name containing serial number, asset tag, and jss id
	deviceInfo = {}
	deviceInfo[device_name] = [ device_serial, device_asset_tag, device_id]

	return deviceInfo


def getMobileDeviceAssetTag(device_id, username, password):
	print "Running refactored getMobileDeviceAssetTag...\n"
	reqStr = jss_api_base_url + '/mobiledevices/id/' + device_id

	#print reqStr

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)
		general = responseXml.find('general')
		asset_tag = general.find('asset_tag').text
		if asset_tag == None:
			asset_tag = 'None'
		# print 'asset tag is {}: '.format(asset_tag)
		return asset_tag
	else:
		return -1

# Search for mobile device, if found AND supervised, return the mobile device JSS id, if not supervised, return -3.
def getSupervisedMobileDeviceId(mobileDeviceName, username, password):
	print "Running refactored getSupervisedMobileDeviceId...\n"
	mobileDeviceName_normalized = urllib2.quote(mobileDeviceName)

	mobile_device_id = getMobileDeviceId(mobileDeviceName, username, password)

	if mobile_device_id == '-1' or mobile_device_id == '-2':
		print 'Please refine your search.'
		return -1
	else:
		reqStr = jss_api_base_url + '/mobiledevices/id/' + mobile_device_id
		r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')
		if r == -1:
			return -1

		#responseCode = r.code
		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)
		#print prettify(responseXml)
		#raise SystemExit

		supervised = responseXml.find('general/supervised').text
		if supervised == 'false':
			return -3
		else:
			return mobile_device_id
