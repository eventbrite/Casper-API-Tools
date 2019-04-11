import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()

def getComputer(computerName, username, password, detail):
	reqStr = jss_api_base_url + '/computers/match/' + computerName
	#print reqStr
	#print detail

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	#print prettify(responseXml)
	#print etree.tostring(responseXml)

	#print 'Response Code: ' + str(responseCode)
	#print 'Root: ' + str(responseXml.tag)
	#print 'Attr: ' + str(responseXml.attrib)

	#for child in responseXml:
	#   print child.tag, child.attrib

	#for computer in responseXml.iter('computer'):
	#   print computer.attrib

	print 'All computers with ' + computerName + ' as part of the computer information:\n'

	for computer in responseXml.findall('computer'):
		name = computer.find('name').text
		asset_tag = computer.find('asset_tag').text
		sn = computer.find('serial_number').text
		mac_addr = computer.find('mac_address').text
		jssID = computer.find('id').text
		#fv2status = computer.find('filevault2_status').text

		#print 'FileVault2 Status: ' + fv2status + '\n'

		if detail == 'yes':
			getComputerByID(jssID, username, password)
		else:
			print 'Computer Name: ' + name
			print 'Asset Number: ' + str(asset_tag)
			print 'Serial Number: ' + sn
			print 'Mac Address: ' + str(mac_addr)
			print 'JSS Computer ID: ' + jssID + '\n'


def getComputerByID(compID, username, password):
	print "Getting computer with JSS ID " + compID + "..."
	reqStr = jss_api_base_url + '/computers/id/' + compID

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
		name = general.find('name').text
		jssID = general.find('id').text
		asset_tag = general.find('asset_tag').text
		sn = general.find('serial_number').text
		mac_addr = general.find('mac_address').text
		last_contact_time = responseXml.find('general/last_contact_time').text
		report_time = responseXml.find('general/report_date').text
		remote_management = general.find('remote_management')
		managed = remote_management.find('managed').text

		print '\nGENERAL INFORMATION:'
		print 'Computer Name: ' + str(name)
		print 'Asset Number: ' + str(asset_tag)
		print 'JSS Computer ID: ' + str(jssID)
		print 'Serial Number: ' + str(sn)
		print 'Mac Address: ' + str(mac_addr)
		print 'Managed: ' + str(managed)
		print 'Last Check-In: ' + str(last_contact_time)
		print 'Last Inventory Update: ' + str(report_time)

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


		hardware = responseXml.find('hardware')
		model = hardware.find('model').text
		modelid = hardware.find('model_identifier').text
		ram = hardware.find('total_ram').text
		ram_gb = int(ram) / 1000
		os_version = hardware.find('os_version').text
		processor_type = hardware.find('processor_type').text
		processor_speed = hardware.find('processor_speed').text

		storage = hardware.find('storage')
		device = storage.find('device')
		disk_size = device.find('size').text
		disk_size_gb = int(disk_size) / 1000
		partition = device.find('partition')
		fv2status = partition.find('filevault2_status').text

		print '\nHARDWARE INFORMATION:'
		print 'Model: ' + model
		print 'Model ID: ' + modelid
		print 'OS X Version: ' + os_version
		print 'Processor: ' + processor_type + ' ' + processor_speed + ' MHz'
		print 'RAM: ' + str(ram_gb) + ' GB'
		print 'Disk Size: ' + str(disk_size_gb) + ' GB'
		print 'FileVault2 Status: ' + str(fv2status)

		extension_attributes = responseXml.find('extension_attributes')
		eas = []

		print '\nEXTENSION ATTRIBUTES:'

		for ea in extension_attributes.findall('extension_attribute'):
			eaName = ea.find('name').text
			eaValue = ea.find('value').text
			eaPair = str(eaName) + ': ' + str(eaValue)
			eas += [ eaPair ]

		print '\n'.join (sorted (eas))


		groups_accounts = responseXml.find('groups_accounts')
		computer_group_memberships = groups_accounts.find('computer_group_memberships')
		#print computer_group_memberships

		groups = []
		for group in computer_group_memberships.findall('group'):
			groupName = group.text
			groups += [ groupName ]
			#print groupName
		print '\nGROUPS: '
		print '\n'.join (sorted (groups))


		local_accounts = groups_accounts.find('local_accounts')
		localusers = []
		for user in local_accounts.findall('user'):
			username = user.find('name').text
			localusers += [ username ]

		print '\nUSERS: '
		print '\n'.join (sorted (localusers))

		print '\n'
		#print prettify(responseXml)

		#print etree.tostring(responseXml)
	else:
		print 'Failed to find computer with JSS ID ' + compID