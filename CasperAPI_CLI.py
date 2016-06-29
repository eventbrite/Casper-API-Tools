#!/usr/bin/python

## Import libraries for basic command line functions
import sys
import getpass
import argparse

import datetime
from datetime import datetime
from datetime import date

import csv
import os, inspect

import urllib2
import base64
import xml.etree.ElementTree as etree

from xml.etree import ElementTree
from xml.dom import minidom

import subprocess

# prettify function from https://pymotw.com/2/xml/etree/ElementTree/create.html
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


### Core Functions

def getJSS_API_URL():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	jss_api_url_Location = scriptPath + '/.jssURL'

	if os.path.isfile(jss_api_url_Location):
		
		with open (jss_api_url_Location) as jssURLfile:
			jssURL = jssURLfile.read().replace('\n','')
			jss_api_url = jssURL + '/JSSResource'
			return jss_api_url

## Base URLs
#jss_api_base_url = getJSS_API_URL()

# Keys Location
#keysfile = '/Volumes/Keys'

def getKeysFile():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	keysFile = scriptPath + '/.keysfile'

	if os.path.isfile(keysFile):
		
		with open (keysFile) as keyLocationFile:
			keysfileLoc = keyLocationFile.read().replace('\n','')
			return keysfileLoc

## Configuration Functions

def resetCLI_Settings():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	encryptedPW_Location = scriptPath + '/.jsspwencrypted'

	if os.path.isfile(encryptedPW_Location):
		os.remove(encryptedPW_Location)
		print "Deleted encrypted password file at " + encryptedPW_Location
	else:
		print "No cached encrypted password file found"

## Functions

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

def setBase_URL():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	orgFileLocation = scriptPath + '/.jssorg'

	if os.path.isfile(orgFileLocation):
		with open (orgFileLocation) as orgFile:
			crowdOrg = orgFile.read().replace('\n','')
	else:
		#No okta org config file found, request JSS org name from user
		crowdOrg = raw_input('Please enter your JSS org URL, in the form company.okta.com: ')
		orgFile = open(orgFileLocation, 'a+')
		orgFile.write(jssOrg)

	## Base URLs
	print api_base_url

	return api_base_url

def getJSSpw():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	apikeyLocation = scriptPath + '/.jsspw'
	#print apikeyLocation

	if os.path.isfile(apikeyLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (apikeyLocation) as apikeyfile:
			api_key = apikeyfile.read().replace('\n','')
			return api_key

	else:
		print "JSS credentials do not exist, prompting..."

		try:
			jss_pw = getpass.getpass('Enter JSS Password:')
			return api_key
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

def decryptString(inputString, salt, passphrase):
    '''Usage: >>> DecryptString("Encrypted String", "Salt", "Passphrase")'''
    p = subprocess.Popen(['/usr/bin/openssl', 'enc', '-aes256', '-d', '-a', '-A', '-S', salt, '-k', passphrase], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    return p.communicate(inputString)[0]

def getSalt():
	keysfile = getKeysFile()
	saltFileLocation = keysfile + '/.jsssalt'

	if os.path.isfile(saltFileLocation):
		with open (saltFileLocation) as saltFile:
			salt = saltFile.read().replace('\n','')
		return salt
	else:
		print 'No keys file available.'
		raise SystemExit

def getPassphrase():
	keysfile = getKeysFile()
	passphraseFileLocation = keysfile + '/.jsspassphrase'

	if os.path.isfile(passphraseFileLocation):
		with open (passphraseFileLocation) as passphraseFile:
			passphrase = passphraseFile.read().replace('\n','')
		return passphrase
	else:
		print 'No keys file available.'
		raise SystemExit

def getEncryptedJSSpw():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	encryptedPWLocation = scriptPath + '/.jsspwencrypted'

	salt = getSalt()
	passphrase = getPassphrase()

	if os.path.isfile(encryptedPWLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (encryptedPWLocation) as encryptedPWfile:
			encryptedPW = encryptedPWfile.read().replace('\n','')
	
		decryptedPW = decryptString(encryptedPW, salt, passphrase)
		return decryptedPW

	else:
		print "JSS credentials do not exist, prompting..."

		try:
			jss_pw = getpass.getpass('Enter JSS Password:')
			return jss_pw
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

## Accounts

def getAccounts(username, password):
	reqStr = jss_api_base_url + '/accounts'

	r = sendAPIRequest(reqStr, username, password, 'GET')

	responseCode = r.code
	responseXml = etree.fromstring(r.read())

	print etree.tostring(responseXml)

	#print 'Root: ' + str(responseXml.tag)

	for users in responseXml.findall('users'):
		for user in users:
			#print "here?"
			name = user.find('name').text
			print name
			#uObj = user.find('user')
			#name = uObj.find('name').text
			#print name


## Computer Functions

def getComputer(computerName, username, password, detail):
	reqStr = jss_api_base_url + '/computers/match/' + computerName
	#print reqStr
	#print detail

	r = sendAPIRequest(reqStr, username, password, 'GET')

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
	#	print child.tag, child.attrib

	#for computer in responseXml.iter('computer'):
	#	print computer.attrib

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
			print 'Mac Address: ' + mac_addr
			print 'JSS Computer ID: ' + jssID + '\n'

def getComputerByID(compID, username, password):
	print "Getting computer with JSS ID " + compID + "..."
	reqStr = jss_api_base_url + '/computers/id/' + compID

	#print reqStr

	r = sendAPIRequest(reqStr, username, password, 'GET')

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
		print 'Computer Name: ' + name
		print 'Asset Number: ' + str(asset_tag)
		print 'JSS Computer ID: ' + jssID
		print 'Serial Number: ' + sn
		print 'Mac Address: ' + mac_addr 
		print 'Managed: ' + managed
		print 'Last Check-In: ' + last_contact_time
		print 'Last Inventory Update: ' + report_time

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


## GROUPS

def GetAllComputerGroups(resource, username, password):
	reqStr = jss_api_base_url + '/computergroups'

	try:
		response = sendAPIRequest(reqStr, username, password, 'GET')
		xmlstring = response.read()
		print str(xmlstring)

		responseCode = str(response.code)
		print responseCode
		#print response.read()

		if '200' in str(responseCode):
			print "Successful API call, printing XML results"
			xml = etree.fromstring(xmlstring)
			#print xml.tag
			#print xml.attrib

			#print etree.tostring(xml)

			print prettify(xml)

			for computer_group in xml.findall('computer_group'):
				name = computer_group.find('name').text
				groupId = computer_group.find('id').text
				is_smart = computer_group.find('is_smart').text
				print name + ' [id: ' + groupId + ', smart: ' + is_smart + ']'
		elif '401' in str(responseCode):
			print "Authorization failed"
	except urllib2.HTTPError, err:
		if '401' in str(err):
			print 'Authorization failed, goodbye.'


def getSerialNumber():
	print 'test'

def unmanageComputer(comp_id, username, password):
	print "Unmanaging computer " + comp_id + "..."
	
	#reqStr = jss_api_base_url + '/computercommands/command/UnmanageDevice'
	#print reqStr

	putStr = jss_api_base_url + '/computers/id/' + comp_id
	#print putStr

	#postXML = "<computers><computer><general><id>" + comp_id + "</id><remote_management><managed>false</managed></remote_management></general></computer></computers>"

	putXML = "<computer><general><remote_management><managed>false</managed></remote_management></general></computer>"
	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to unmanage computer ID ' + comp_id + '. Make sure the computer actually exists in the JSS.'
	else:
		responseCode = str(response.code)
		#print 'Response Code: ' + responseCode
		if responseCode == '201':
			print 'Successfully unmanaged computer ID ' + comp_id + '...'
			
		
		## Uncomment this part to see the xml response
		#xmlstring = response.read()
		#xml = etree.fromstring(xmlstring)
		#print prettify(xml)

def updateAssetTag(comp_id, asset_tag, username, password):
	print 'Updating asset tag for computer ID ' + comp_id + ' with asset tag ' + asset_tag + '...'

	putStr = jss_api_base_url + '/computers/id/' + comp_id
	#print putStr

	putXML = "<computer><general><asset_tag>" + asset_tag + "</asset_tag></general></computer>"
	response = sendAPIRequest(putStr, username, password, 'PUT', putXML)

	if response == -1:
		print 'Failed to update asset tag for computer ' + comp_id + ', see error above.'
		return
	else:
		print 'Successfully updated asset tag for computer ' + comp_id + '.'

def unmanageComputerIDsFromCSV(computersCSV, username, password):

	# CSV file with one column, just JSS computer IDs

	with open (computersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(computerreader, None)

		for row in computerreader:
			compID = row[0].replace('"', '').strip()
			#print 'Test Run: Unmanage computer ID ' + compID
			unmanageComputer(compID, username, password)

def deleteComputerByID(comp_id, username, password):
	
	getComputerByID(comp_id, username, password)

	sure = raw_input('Are you sure you want to delete the computer above from the JSS? (y/n): ')

	if sure == 'y':	
		print "Deleting computer " + comp_id + "..."

		delStr = jss_api_base_url + '/computers/id/' + comp_id
		#print delStr
		response = sendAPIRequest(delStr, username, password, 'DELETE')

		if response == -1:
			print 'Failed to delete computer. See errors above.'
		else:
			print 'Successfully deleted computer ' + comp_id

	else:
		print 'Aborting request to delete computer ' + comp_id

		## Uncomment this part to see the xml response
		#xmlstring = response.read()
		#xml = etree.fromstring(xmlstring)
		#print prettify(xml)

		#responseCode = str(response.code)
		#print 'Response Code: ' + responseCode

def deleteComputerIDsFromCSV(computersCSV, username, password):

	# CSV file with one column, just JSS computer IDs

	with open (computersCSV, 'rU') as csvfile:
		computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(computerreader, None)

		for row in computerreader:
			compID = row[0].replace('"', '').strip()
			print 'Test Run: Delete computer ID ' + compID
			deleteComputerByID(compID, username, password)


def getComputerCommands(username, password):
	print "Getting computer commands..."
	reqStr = jss_api_base_url + '/computercommands'
	#print reqStr

	r = sendAPIRequest(reqStr, username, password, 'GET')
	print r

	responseCode = r.code
	print 'Response code: ' + str(responseCode)

	responseXml = etree.fromstring(r.read())

	print etree.tostring(responseXml)

	#responseXml = etree.fromstring(r.read())
	#print prettify(responseXml)
	#print etree.tostring(responseXml)

def getJSSUsername():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	jssusernameLocation = scriptPath + '/.jssusername'
	#print apikeyLocation

	if os.path.isfile(jssusernameLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (jssusernameLocation) as jssusernamefile:
			jss_username = jssusernamefile.read().replace('\n','')
			return jss_username

	else:
		print "JSS Username does not exist, prompting for JSS username"

		try:
			jss_username = raw_input('JSS Username: ')
			return jss_username
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

def getJSSPassword():
	## This method supports a plaintext password stored in the file .jsspassword existing in the same directory
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	jsspasswordLocation = scriptPath + '/.jsspassword'
	#print apikeyLocation

	if os.path.isfile(jsspasswordLocation):
		#print "api key file exists, here's the key!"
		
		#print "Path: " + os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

		with open (jsspasswordLocation) as jsspasswordfile:
			jss_password = jsspasswordfile.read().replace('\n','')
			return jss_password

	else:
		print "JSS Password does not exist, prompting for key"

		try:
			jss_password = getpass.getpass('JSS Password: ')
			return jss_password
		except:
			print "\nCtrl-C detected, exiting..."
			raise SystemExit

def main():

	### Start here
	#user = raw_input('JSS Username: ')
	#password = getpass.getpass('Password: ')

	user = getJSSUsername()
	#password = getJSSPassword()
	password = getEncryptedJSSpw()



	unmanageComputerHelp = 'JSS Computer ID'

	parser = argparse.ArgumentParser(description='Interact with the Casper JSS API')
	subparsers = parser.add_subparsers(help='Enter command with -h for help on each particular command')
	'''
	parser_config = subparsers.add_parser('config', help='Casper CLI Configuration options')
	parser_config.set_defaults(which='config')
	parser_config.add_argument('-o', '--option', metavar='', choices=['Reset', 'Setup'], help='Enter Reset to reset the CLI to default settings, enter Setup to configure the Casper CLI')
	'''
	parser_deletecomputerbyid = subparsers.add_parser('deletecomputerbyid', help='Delete computer by JSS ID')
	parser_deletecomputerbyid.set_defaults(cmd='deletecomputerbyid')
	parser_deletecomputerbyid.add_argument('computerID', help=unmanageComputerHelp)
	parser_deletecomputeridsfromcsv = subparsers.add_parser('deletecomputeridsfromcsv', help='Delete computers from JSS IDs in CSV file')
	parser_deletecomputeridsfromcsv.set_defaults(cmd='deletecomputeridsfromcsv')
	parser_deletecomputeridsfromcsv.add_argument('csvfile', help='Full path to CSV file with one column containing JSS computer IDs to delete')
	parser_getcomputer = subparsers.add_parser('getcomputer', help='Search for a computer')
	parser_getcomputer.set_defaults(cmd='getcomputer')
	parser_getcomputer.add_argument('compsearch', help='Search string for computer')
	parser_getcomputer.add_argument('-d', '--detail', default='no', help='Print detailed computer info')
	parser_getcomputerbyid = subparsers.add_parser('getcomputerbyid', help='Get computer by ID')
	parser_getcomputerbyid.set_defaults(cmd='getcomputerbyid')
	parser_getcomputerbyid.add_argument('computerID', help=unmanageComputerHelp)
	parser_unmanagecomputer = subparsers.add_parser('unmanagecomputer', help='Get user object')
	parser_unmanagecomputer.set_defaults(cmd='unmanagecomputer')
	parser_unmanagecomputer.add_argument('computerID', help=unmanageComputerHelp)
	parser_unmanagecomputeridsfromcsv = subparsers.add_parser('unmanagecomputeridsfromcsv', help='Unmanage computers from JSS IDs in CSV file')
	parser_unmanagecomputeridsfromcsv.set_defaults(cmd='unmanagecomputeridsfromcsv')
	parser_unmanagecomputeridsfromcsv.add_argument('csvfile', help='Full path to CSV file with one column containing JSS computer IDs to unmanage')
	parser_updateassettag = subparsers.add_parser('updateassettag', help='Update Asset Tag')
	parser_updateassettag.set_defaults(cmd='updateassettag')
	parser_updateassettag.add_argument('computerID', help='JSS Computer ID')
	parser_updateassettag.add_argument('assetTag', help='Asset Tag')


	args = parser.parse_args()

	APIcommand = args.cmd

	#print parser.parse_args()
	#print "Script: " + __file__
	scriptName = inspect.getfile(inspect.currentframe())
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

	## CONFIGURATION SETTINGS

	'''if APIcommand == 'config':
		option = args.option
		if str(option) == 'Reset':
			resetCLI_Settings()
			raise SystemExit
		elif option == 'Setup':
			setupCasperCLI()
			print 'Setup complete.'
			raise SystemExit'''


	## MAIN BODY

	if APIcommand == 'deletecomputerbyid':
		computerID = args.computerID
		deleteComputerByID(computerID, user, password)
	elif APIcommand == 'deletecomputeridsfromcsv':
		computersCSV = args.csvfile
		deleteComputerIDsFromCSV(computersCSV, user, password)
	elif APIcommand == 'getcomputer':
		compSearch = args.compsearch
		detail = args.detail
		getComputer(compSearch, user, password, detail)
	elif APIcommand == 'getcomputerbyid':
		computerID = args.computerID
		getComputerByID(computerID, user, password)
	elif APIcommand == "unmanagecomputer":
		computerID = args.computerID
		unmanageComputer(computerID, user, password)
	elif APIcommand == 'unmanagecomputeridsfromcsv':
		computersCSV = args.csvfile
		unmanageComputerIDsFromCSV(computersCSV, user, password)
	elif APIcommand == 'updateassettag':
		computerID = args.computerID
		assetTag = args.assetTag
		updateAssetTag(computerID, assetTag, user, password)
	else:
		print 'Unknown command.'

if __name__ == '__main__':
	## Set the JSS API URL
	jss_api_base_url = getJSS_API_URL()

	## Run the main parser and command line interface
	main()
