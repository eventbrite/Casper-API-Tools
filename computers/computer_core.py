import sys
sys.path.append('..')
import urllib2
import requests
import csv
from csv import writer, DictReader, DictWriter
from utilities import jamfconfig
from utilities import apirequests
from computergroups import computergroups
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()


def getAllComputersBasic(username, password):
	''' Query Jamf API for all Computers using the Basic Subset query to return limited details on each, create dictionary, return dict for iteration in other methods '''

	reqStr = jss_api_base_url + '/computers/subset/basic'
	compsBasicDict = {}

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	baseXml = r.read()
	# print baseXml
	responseXml = etree.fromstring(baseXml)

	# computers = responseXml.find('computers')

	for comp in responseXml.findall('computer'):
		compname = comp.find('name').text
		jssID = comp.find('id').text
		compsBasicDict.update({jssID: compname})

	return compsBasicDict


def findComputer(computerName, username, password, detail):
	''' Companion Function for use in other methods to lookup computer in JSS by search string (username) and return matching records as a list of JSS IDs '''

	reqStr = jss_api_base_url + '/computers/match/' + computerName
	compMatches = []

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	#responseCode = r.code
	baseXml = r.read()
	#print baseXml
	responseXml = etree.fromstring(baseXml)

	if responseXml:
		print 'All computers with ' + computerName + ' as part of the computer information:\n'

		for computer in responseXml.findall('computer'):
			name = computer.find('name').text
			asset_tag = computer.find('asset_tag').text
			sn = computer.find('serial_number').text
			mac_addr = computer.find('mac_address').text
			jssID = computer.find('id').text
			#fv2status = computer.find('filevault2_status').text
			compMatches.append(jssID)

			print 'Computer Name: ' + name
			print 'Asset Number: ' + str(asset_tag)
			print 'Serial Number: ' + sn
			print 'Mac Address: ' + str(mac_addr)
			print 'JSS Computer ID: ' + jssID + '\n'

		return compMatches

	else:
		print "No computer matches found"
		return None


def getComputer(computerName, username, password, detail):
	print 'Running refactored getComputer ...\n'
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


def getComputerId(computerSearch, username, password):
	print 'Running refactored getComputerId...\n'
	computerSearch_normalized = urllib2.quote(computerSearch)

	reqStr = jss_api_base_url + '/computers/match/' + computerSearch_normalized

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
		return responseXml.find('computer/id').text
	else:
		#print 'Too many results, narrow your search paramaters.'
		return -2


def getUserEmailByComputerID(compID, username, password):
	print 'Running refactored getUserEmailByComputerID...\n'
	reqStr = jss_api_base_url + '/computers/id/' + compID
	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != 1:
		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)
		email_address = responseXml.find('location/email_address').text
		return email_address
	else:
		return -1


def getComputerByID(compID, username, password):
	print 'Running refactored getComputerByID...\n'
	print "Getting computer with JSS ID " + compID + "..."
	reqStr = jss_api_base_url + '/computers/id/' + compID

	#print reqStr

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:
		try:
			responseCode = r.code

			#print 'Response Code: ' + str(responseCode)

			baseXml = r.read()
			#print baseXml
			responseXml = etree.fromstring(baseXml)

			#print responseXml.tag

			general = responseXml.find('general')
			name = general.find('name').text
			strName = name.encode('utf8', 'replace')
			jssID = general.find('id').text
			asset_tag = general.find('asset_tag').text
			sn = general.find('serial_number').text
			mac_addr = general.find('mac_address').text
			last_contact_time = responseXml.find('general/last_contact_time').text
			report_time = responseXml.find('general/report_date').text
			remote_management = general.find('remote_management')
			managed = remote_management.find('managed').text

			print '\nGENERAL INFORMATION:'
			print 'Computer Name: ' + strName
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

		except UnicodeEncodeError as error:
			print 'There was a problem parsing the data, likely an invalid character in one of the fields.\n'
			print error

		except AttributeError as error:
			print 'There was a problem parsing the data, a required field may have a null value.\n'
			print error

	else:
		print 'Failed to find computer with JSS ID ' + compID


def getComputerbyLastUser(searchStr, username, password):
	''' Backup search companion function to do api search for computer ID by matching 'Last User' field.  May require recursive search through all computers.  Returns jss id '''
	compMatches = []

	# API url for Jamf report containing last user attribute on all active
	lastuserReportURL = jss_api_base_url + "/advancedcomputersearches/id/43"
	reportJson = apirequests.sendAPIGetRequest(lastuserReportURL, username, password, 'GET')

	# Iterate over all computer IDs in reportJSON, lookup "last user" and see if matches, return compIDs if found
	for k,v in reportJson.items():
		if k == "advanced_computer_search":
			reportDict = v
			for k,v in reportDict.items():
				if k == "computers":
					compList = v

	for listDict in compList:
		if listDict["Last_User"] == searchStr:
			compMatches.append(listDict["id"])


	if compMatches:
		print "\nFound the Following Computers with {} as the Last User:\n".format(searchStr)
		for comp in compMatches:
			print comp
		print "\n"
		return compMatches

	else:
		print "\nNo Computer matches with {} found in either the Computer Name or the Last_User fields.".format(searchStr)
		return None


def getCompwithUserinName(searchStr, username, password):
	'''Function runs the computers basic subset function, iterates on returned dictionary to see if username is in any of the computer name fields, then returns the results as a list'''

	# Get All Computers Dict - subset basic (returns JSS IDs and computer names)
	compsDict = getAllComputersBasic(username, password)
	compMatches = []

	# Narrow down search to see if any with matching username as part of computer name
	print "\nSearching for {} in all Computer name fields...\n".format(searchStr)

	for k,v in compsDict.items():
		if searchStr in v:
			compMatches.append(k)
			print "found a match! computer ID:  {}".format(k)

	if compMatches:
		return compMatches
	else:
		print "No computer name matches found for {}, moving along...".format(searchStr)



def getCompLocalAccounts(compID, username, password):
	''' Companion function for use in other methods, to look up Local accounts listed for JSS comp ID, and return usernames as list '''

	reqStr = jss_api_base_url + '/computers/id/' + compID
	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != 1:
		baseXml = r.read()
		#print baseXml
		responseXml = etree.fromstring(baseXml)
		groups_accounts = responseXml.find('groups_accounts')
		local_accounts = groups_accounts.find('local_accounts')
		localusers = []
		for user in local_accounts.findall('user'):
			uname = user.find('name').text
			localusers.append(uname)
		return localusers
	else:
		return -1


def addComputerToGroup(computer, computer_group, username, password):
	print 'Running refactored addComputerToGroup...\n'
	# Find computer JSS ID
	computer_id = getComputerId(computer, username, password)

	if str(computer_id) == '-1':
		print 'Computer ' + computer + ' not found, please try again.'
		return
	elif str(computer_id) == '-2':
		print 'More than one computer found matching search string ' + computer + ', please try again.'
		return

	# Find computer group JSS ID
	computer_group_id = computergroups.getComputerGroupId(computer_group, username, password)
	if str(computer_group_id) == '-1':
		print 'Computer group ' + computer_group + ' not found, please try again.'
		return

	print 'Adding computer id ' + str(computer_id) + ' to computer group id ' + str(computer_group_id)

	putStr = jss_api_base_url + '/computergroups/id/' + str(computer_group_id)
	putXML = '<computer_group><computer_additions><computer><id>' + str(computer_id) + '</id></computer></computer_additions></computer_group>'

	#print putStr
	#print putXML
	#return

	response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to add computer ' + computer + ' to group, see error above.'
		return
	else:
		print 'Successfully added computer ' + computer + ' to group ' + computer_group + '.'


def addCompstoGroupfromCSV(compsCSV, computer_group, username, password):
	''' Function takes in csv file with computer JSS IDs and iterates list and adds to computer group from provided argument '''

	computer_group_id = computergroups.getComputerGroupId(computer_group, username, password)
	if str(computer_group_id) == '-1':
		print 'Computer group ' + computer_group + ' not found, please try again.'
		return

	compsList = []

	with open (compsCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(computerreader, None)

		for row in computerreader:
			jssID = row[0].replace('"', '').strip()
			compsList.append(jssID)

	print '\nAbout to process the following computer JSS IDs: \n'
	for comp in compsList:
		print comp
	print '\nProcessing {} Computer IDs...\n'.format(len(compsList))

	# add to selected JSS group
	for comp in compsList:
		print 'Adding computer id ' + str(comp) + ' to computer group id ' + str(computer_group_id)

		putStr = jss_api_base_url + '/computergroups/id/' + str(computer_group_id)
		putXML = '<computer_group><computer_additions><computer><id>' + str(comp) + '</id></computer></computer_additions></computer_group>'

		response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

		if response == -1:
			print 'Failed to add computer ' + comp + ' to group, see error above.'
			return
		else:
			print 'Successfully added computer ' + comp + ' to group ' + computer_group + '.'



def removeComputerFromGroup(computer, computer_group, username, password):
	print 'Running refactored removeComputerFromGroup...\n'
	# Find computer JSS ID
	computer_id = getComputerId(computer, username, password)

	if str(computer_id) == '-1':
		print 'Computer ' + computer + ' not found, please try again.'
		return
	elif str(computer_id) == '-2':
		print 'More than one computer found matching search string ' + computer + ', please try again.'
		return

	# Find computer group JSS ID
	computer_group_id = computergroups.getComputerGroupId(computer_group, username, password)
	if str(computer_group_id) == '-1':
		print 'Computer group ' + computer_group + ' not found, please try again.'
		return

	print 'Removing computer id ' + str(computer_id) + ' from computer group id ' + str(computer_group_id)

	putStr = jss_api_base_url + '/computergroups/id/' + str(computer_group_id)
	putXML = '<computer_group><computer_deletions><computer><id>' + str(computer_id) + '</id></computer></computer_deletions></computer_group>'

	#print putStr
	#print putXML
	#return

	response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to remove computer ' + computer + ' from group, see error above.'
		return
	else:
		print 'Successfully removed computer ' + computer + ' from group ' + computer_group + '.'


def updateAssetTag(comp_id, asset_tag, username, password):
	print 'Running refactored updateAssetTag...\n'
	print 'Updating asset tag for computer ID ' + comp_id + ' with asset tag ' + asset_tag + '...'

	putStr = jss_api_base_url + '/computers/id/' + comp_id
	#print putStr

	putXML = "<computer><general><asset_tag>" + asset_tag + "</asset_tag></general></computer>"
	response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to update asset tag for computer ' + comp_id + ', see error above.'
		return
	else:
		print 'Successfully updated asset tag for computer ' + comp_id + '.'


def updateComputerUserInfo(comp_id, username, real_name, email_address, position, phone, department, building, room, overwrite, jssuser, jsspassword):
	print 'Running refactored updateComputerUserInfo...\n'


	putStr = jss_api_base_url + '/computers/id/' + comp_id
	if overwrite == 'y':
		print 'Overwriting all existing user and location info for computer ID ' + comp_id + ' with the following:\n' + '\n  Username: ' + username + '\n  Full Name: ' + real_name + '\n  Email: ' + email_address + '\n  Position: ' + position + '\n  Phone: ' + str(phone) + '\n  Department: ' + department + '\n  Building: ' + building + '\n  Room: ' + room + '\n'
		putXML = "<computer><location><username>" + username + "</username><real_name>" + real_name + "</real_name><email_address>" + email_address + "</email_address><position>" + position + "</position><phone>" + str(phone) + "</phone><department>" + department + "</department><building>" + building + "</building><room>" + room + "</room></location></computer>"
	else:
		updateStr = 'Updating user and location info for computer ID ' + comp_id + ' with the following:\n'
		putXML = "<computer><location>"
		updateCount = 0

		if username != '':
			putXML += '<username>' + username + '</username>'
			updateStr += '\n  Username : ' + username
			updateCount += 1

		if real_name != '':
			putXML += '<real_name>' + real_name + '</real_name>'
			updateStr += '\n Full Name: ' + real_name
			updateCount += 1

		if email_address != '':
			putXML += '<email_address>' + email_address + '</email_address>'
			updateStr += '\n  Email: ' + email_address
			updateCount += 1

		if position != '':
			putXML += '<position>' + position + '</position>'
			updateStr += '\n  Position: ' + position
			updateCount += 1

		if phone != '':
			putXML += '<phone>' + str(phone) + '</phone>'
			updateStr += '\n  Phone: ' + str(phone)
			updateCount += 1

		if department != '':
			putXML += '<department>' + department + '</department>'
			updateStr += '\n  Department: ' + department
			updateCount += 1

		if building != '':
			putXML += '<building>' + building + '</building>'
			updateStr += '\n  Building: ' + building
			updateCount += 1

		if room != '':
			putXML += '<room>' + room + '</room>'
			updateStr += '\n  Room: ' + room
			updateCount += 1

		putXML += "</location></computer>"

		if updateCount == 0:
			# Nothing to update
			print "Nothing to update."
			return


	#print putXML

	response = apirequests.sendAPIRequest(putStr, jssuser, jsspassword, 'PUT', putXML)

	if response == -1:
		print 'Failed to update user and location info for computer ' + comp_id + ', see error above.'
		return
	else:
		print 'Successfully updated user and location info for computer ' + comp_id + '.\n'


def updateComputerUserInfoFromCSV(computersCSV, username, password):
	print 'Running refactored updateComputerUserInfoFromCSV...\n'

	# CSV File with 9 columns: JSS Computer ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite

	with open (computersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(computerreader, None)

		for row in computerreader:
			compID = row[0].replace('"', '').strip()
			uName = row[1].replace('"', '').strip()
			fullName = row[2].replace('"', '').strip()
			email = row[3].replace('"', '').strip()
			position = row[4].replace('"', '').strip()
			phone = row[5].replace('"', '').strip()
			department = row[6].replace('"', '').strip()
			building = row[7].replace('"', '').strip()
			room = row[8].replace('"', '').strip()
			overwrite = row[9].replace('"', '').strip()

			print 'Update computer user info with ' + 'JSS ID: ' + compID + ' Username: ' + uName + ' Full Name: ' + fullName + ' Email: ' + email + ' Position: ' + position + ' Phone: ' + str(phone) + ' Dept: ' + department + 'Bldg: ' + building + ' Room: ' + room + ' Overwrite: ' + overwrite
			updateComputerUserInfo(compID, uName, fullName, email, position, phone, department, building, room, overwrite, username, password)
	return


def getComputersforUsersFromCSV(usersCSV, outputCSV, username, password):
	''' Function takes in CSV with user email addresses and runs a lookup for associated computers.  Returns Dictionary of Computer info and exports to CSV '''
	userList = []
	notFound = []

	with open (usersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		next(computerreader, None)

		for row in computerreader:
			email = row[0].replace('"', '').strip()
			userList.append(email)

	print '\nAbout to run a computer lookup on the following email addresses: \n'
	for email in userList:
		print email
	print '\nProcessing {} Email Addresses\n'.format(len(userList))

	# Open output CSV for updating, Iterate through list of Email addresses and lookup associated computer details, write to CSV

	csvHeaders = ['email','name','asset_tag','sn','mac_addr','jssID']

	with open(outputCSV, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=csvHeaders)
		writer.writeheader()

		for email in userList:
			print '\nLooking up computers for {}...'.format(email)
			dataDict = {}
			reqStr = jss_api_base_url + '/computers/match/' + email

			try:
				r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

				if r == -1:
					return

				#responseCode = r.code
				baseXml = r.read()
				#print baseXml
				responseXml = etree.fromstring(baseXml)

				# print 'All computers with ' + computerName + ' as part of the computer information:\n'

				for computer in responseXml.findall('computer'):
					name = computer.find('name').text
					asset_tag = computer.find('asset_tag').text
					sn = computer.find('serial_number').text
					mac_addr = computer.find('mac_address').text
					jssID = computer.find('id').text
					# Create the Dictionary
					dataDict.update({'email':email})
					dataDict.update({'name':name})
					dataDict.update({'asset_tag':asset_tag})
					dataDict.update({'sn':sn})
					dataDict.update({'mac_addr':mac_addr})
					dataDict.update({'jssID':jssID})

				if not dataDict:
					print 'No computers found for {}, moving on...'.format(email)
					notFound.append(email)
				else:
					# write row to CSV
					writer.writerow(dataDict)


			except UnicodeEncodeError as error:
				print 'There was a problem parsing the data, likely an invalid character in one of the fields.\n'
				print error

			except AttributeError as error:
				print 'There was a problem parsing the data, a required field may have a null value.\n'
				print error


	print '\nComputers CSV has been created at {}.  All Done.'.format(outputCSV)

	print '\nWas unable to find computers for the following user email addresses:\n'
	for email in notFound:
		print email





