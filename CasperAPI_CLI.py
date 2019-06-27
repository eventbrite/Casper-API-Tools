#!/usr/bin/python
# Casper API Tools version 0.3.0

##############################################################
##############################################################
#
# Casper API Tools Command Line Inteface
# https://github.com/eventbrite/Casper-API-Tools
# Original Script created by: Jason Kuo
# Updated 06/19/2019
#
##############################################################
##############################################################

## Import libraries for basic command line functions
import sys
import getpass
import argparse

import datetime
from datetime import datetime
from datetime import date

import csv
from csv import writer, DictWriter
import os, inspect

import urllib2
import base64
import xml.etree.ElementTree as etree

from xml.etree import ElementTree
from xml.dom import minidom

import subprocess

## Import locally created libraries

from policies import policies_core
from policies import policies_extended
from computers import computer_core
from computers import computer_ea
from computers import computer_lifecycle
from computergroups import computergroups
from mobiledevices import mobiledevices
from mobiledevices import mobiledevice_core
from mobiledevices import mobiledevice_lifecycle
from mobiledevices import mobiledevicegroups

__version__ = '0.3.0'

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

def cleanupOutput(inputString):
	#print str(inputString)
	return inputString.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", "\"").replace(u"\u201d", "\"")


def getSerialNumber():
	print 'test'


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
	parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
	'''
	parser_config = subparsers.add_parser('config', help='Casper CLI Configuration options')
	parser_config.set_defaults(which='config')
	parser_config.add_argument('-o', '--option', metavar='', choices=['Reset', 'Setup'], help='Enter Reset to reset the CLI to default settings, enter Setup to configure the Casper CLI')
	'''

	parser_addcomputertogroup = subparsers.add_parser('addcomputertogroup', help='Add computer to group')
	parser_addcomputertogroup.set_defaults(cmd='addcomputertogroup')
	parser_addcomputertogroup.add_argument('computerSearch', help='Computer to add')
	parser_addcomputertogroup.add_argument('computerGroupSearch', help='Computer group to add computer to')

	parser_addmobiledevicetogroup = subparsers.add_parser('addmobiledevicetogroup', help='Add mobile device to group')
	parser_addmobiledevicetogroup.set_defaults(cmd='addmobiledevicetogroup')
	parser_addmobiledevicetogroup.add_argument('mobileSearch', help='Mobile Device to add')
	parser_addmobiledevicetogroup.add_argument('mobileGroupSearch', help='Mobile Device group to add device to')

	parser_clearmobiledevicepasscode = subparsers.add_parser('clearmobiledevicepasscode', help='Clear mobile device passcode for specified device')
	parser_clearmobiledevicepasscode.set_defaults(cmd='clearmobiledevicepasscode')
	parser_clearmobiledevicepasscode.add_argument('mobileSearch', help='Mobile Device to clear passcode for')

	parser_deletecomputerbyid = subparsers.add_parser('deletecomputerbyid', help='Delete computer by JSS ID')
	parser_deletecomputerbyid.set_defaults(cmd='deletecomputerbyid')
	parser_deletecomputerbyid.add_argument('computerID', help=unmanageComputerHelp)

	parser_deletecomputeridsfromcsv = subparsers.add_parser('deletecomputeridsfromcsv', help='Delete computers from JSS IDs in CSV file')
	parser_deletecomputeridsfromcsv.set_defaults(cmd='deletecomputeridsfromcsv')
	parser_deletecomputeridsfromcsv.add_argument('csvfile', help='Full path to CSV file with one column containing JSS computer IDs to delete')

	parser_deletemobiledevicebyid = subparsers.add_parser('deletemobiledevicebyid', help='Delete mobile device by JSS ID')
	parser_deletemobiledevicebyid.set_defaults(cmd='deletemobiledevicebyid')
	parser_deletemobiledevicebyid.add_argument('mobiledeviceID', help='Delete mobile device by id')

	parser_findmobiledeviceid = subparsers.add_parser('findmobiledeviceid', help='Find mobile device JSS ID using search string')
	parser_findmobiledeviceid.set_defaults(cmd='findmobiledeviceid')
	parser_findmobiledeviceid.add_argument('searchString', help='String to search for, followed by * for wildcard')

	parser_getcomputer = subparsers.add_parser('getcomputer', help='Search for a computer')
	parser_getcomputer.set_defaults(cmd='getcomputer')
	parser_getcomputer.add_argument('compsearch', help='Search string for computer')
	parser_getcomputer.add_argument('-d', '--detail', default='no', help='Print detailed computer info')
	parser_getcomputerbyid = subparsers.add_parser('getcomputerbyid', help='Get computer by ID')
	parser_getcomputerbyid.set_defaults(cmd='getcomputerbyid')
	parser_getcomputerbyid.add_argument('computerID', help=unmanageComputerHelp)
	parser_getcomputerextensionattributes = subparsers.add_parser('getcomputerextensionattributes', help='Get computer Extension Attributes by ID')
	parser_getcomputerextensionattributes.set_defaults(cmd='getcomputerextensionattributes')
	parser_getcomputerextensionattributes.add_argument('computerID', help='Get computer Extension Attributes by JSS ID')

	parser_getcomputergroupid = subparsers.add_parser('getcomputergroupid', help='Get computer group JSS ID')
	parser_getcomputergroupid.set_defaults(cmd='getcomputergroupid')
	parser_getcomputergroupid.add_argument('groupsearch', help='Search string for computer group')

	parser_getcomputergroupmembers = subparsers.add_parser('getcomputergroupmembers', help='Get computer group members')
	parser_getcomputergroupmembers.set_defaults(cmd='getcomputergroupmembers')
	parser_getcomputergroupmembers.add_argument('groupsearch', help='Search string for computer group')

	parser_getmobiledevice = subparsers.add_parser('getmobiledevice', help='Search for a mobile device')
	parser_getmobiledevice.set_defaults(cmd='getmobiledevice')
	parser_getmobiledevice.add_argument('mobilesearch', help='Search string for mobile device')
	parser_getmobiledevice.add_argument('-d', '--detail', default='no', help='Print detailed mobile device info')
	parser_getmobiledevicebyid = subparsers.add_parser('getmobiledevicebyid', help='Get mobile device by ID')
	parser_getmobiledevicebyid.set_defaults(cmd='getmobiledevicebyid')
	parser_getmobiledevicebyid.add_argument('mobileDeviceID', help='Mobile Device JSS ID')
	parser_getmobiledevicegroup = subparsers.add_parser('getmobiledevicegroup', help='Search for a mobile device group')
	parser_getmobiledevicegroup.set_defaults(cmd='getmobiledevicegroup')
	parser_getmobiledevicegroup.add_argument('mobilegroupsearch', help='Search string for mobile device group')

	parser_getmobiledevicescsv = subparsers.add_parser('getmobiledevicescsv', help='Search for all mobile devices in a CSV file containing one column with search strings')
	parser_getmobiledevicescsv.set_defaults(cmd='getmobiledevicescsv')
	parser_getmobiledevicescsv.add_argument('csvfile', help='Full path to CSV file with one column containing mobile device search strings')

	parser_getallcomputergroups = subparsers.add_parser('getallcomputergroups', help='Get all Computer Groups in JSS')
	parser_getallcomputergroups.set_defaults(cmd='getallcomputergroups', help='lists all computer groups in JSS')

	parser_getallpolicies = subparsers.add_parser('getallpolicies', help='Get all policies in the JSS')
	parser_getallpolicies.set_defaults(cmd='getallpolicies', help='Get all policies in the JSS')

	parser_getpolicybyid = subparsers.add_parser('getpolicybyid', help='Find specific policy information by JSS ID')
	parser_getpolicybyid.set_defaults(cmd='getpolicybyid')
	parser_getpolicybyid.add_argument('policyid', help='ID number for the JSS Policy.  If uncertain, run getallpolicies to see entire list')

	parser_getenabledpolicies = subparsers.add_parser('getenabledpolicies', help='Get all currently enabled policies')
	parser_getenabledpolicies.set_defaults(cmd='getenabledpolicies')

	parser_getenabledpoliciestocsv = subparsers.add_parser('getenabledpoliciestocsv', help='Get all currently enabled policy names exported to CSV')
	parser_getenabledpoliciestocsv.set_defaults(cmd='getenabledpoliciestocsv')

	parser_getpoliciesscopedtogroup = subparsers.add_parser('getpoliciesscopedtogroup', help='Get the enabled policies scoped to a specific Computer Group ID')
	parser_getpoliciesscopedtogroup.set_defaults(cmd='getpoliciesscopedtogroup')
	parser_getpoliciesscopedtogroup.add_argument('groupid', help='ID number for the Computer Group. If uncertain, run getallcomputergroups to see entire list')

	parser_lockmobiledevice = subparsers.add_parser('lockmobiledevice', help='Lock a single mobile device')
	parser_lockmobiledevice.set_defaults(cmd='lockmobiledevice')
	parser_lockmobiledevice.add_argument('mobileSearch', help='Mobile Device to issue lock command to')

	parser_lockmobiledevicescsv = subparsers.add_parser('lockmobiledevicescsv', help='Lock multiple devices as listed on csv')
	parser_lockmobiledevicescsv.set_defaults(cmd='lockmobiledevicescsv')
	parser_lockmobiledevicescsv.add_argument('csvfile', help='Full path to CSV file with one column containing mobile device search strings')

	parser_removecomputerfromgroup = subparsers.add_parser('removecomputerfromgroup', help='Remove a computer from a group')
	parser_removecomputerfromgroup.set_defaults(cmd='removecomputerfromgroup')
	parser_removecomputerfromgroup.add_argument('computerSearch', help='Computer to remove')
	parser_removecomputerfromgroup.add_argument('computerGroupSearch', help='Computer group to remove computer from')

	parser_removemobiledevicefromgroup = subparsers.add_parser('removemobiledevicefromgroup', help='Remove a mobile device from a group')
	parser_removemobiledevicefromgroup.set_defaults(cmd='removemobiledevicefromgroup')
	parser_removemobiledevicefromgroup.add_argument('mobileSearch', help='Mobile Device to remove')
	parser_removemobiledevicefromgroup.add_argument('mobileGroupSearch', help='Mobile Device group to remove device from')

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
	parser_updatecomputeruserinfo = subparsers.add_parser('updatecomputeruserinfo', help='Update User and Location Info')
	parser_updatecomputeruserinfo.set_defaults(cmd='updatecomputeruserinfo')
	parser_updatecomputeruserinfo.add_argument('computerID', help='JSS Computer ID')
	parser_updatecomputeruserinfo.add_argument('-u', '--username', default='', help='Username')
	parser_updatecomputeruserinfo.add_argument('-n', '--real_name', default='', help='Real Name')
	parser_updatecomputeruserinfo.add_argument('-e', '--email_address', default='', help='Email Address')
	parser_updatecomputeruserinfo.add_argument('-p', '--position', default='', help='Position')
	parser_updatecomputeruserinfo.add_argument('-t', '--phone', default='', help='Phone Number')
	parser_updatecomputeruserinfo.add_argument('-d', '--department', default='', help='Department')
	parser_updatecomputeruserinfo.add_argument('-b', '--building', default='', help='Building')
	parser_updatecomputeruserinfo.add_argument('-r', '--room', default='', help='Room')
	parser_updatecomputeruserinfo.add_argument('-o', '--overwrite', default='n', help='Overwrite all existing values [y] or update only [n]. Default is no')
	parser_updatecomputeruserinfofromcsv = subparsers.add_parser('updatecomputeruserinfofromcsv', help='Update Computer User and Location Info from JSS IDs in CSV file')
	parser_updatecomputeruserinfofromcsv.set_defaults(cmd='updatecomputeruserinfofromcsv')
	parser_updatecomputeruserinfofromcsv.add_argument('csvfile', help='Full path to CSV File with 9 columns: JSS Computer ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite')

	parser_updatemobileassettag = subparsers.add_parser('updatemobileassettag', help='Update Mobile Asset Tag')
	parser_updatemobileassettag.set_defaults(cmd='updatemobileassettag')
	parser_updatemobileassettag.add_argument('mobileSearch', help='Mobile Device to add asset tag to')
	parser_updatemobileassettag.add_argument('assetTag', help='Asset Tag')

	parser_updatemobileassettagcsv = subparsers.add_parser('updatemobileassettagcsv', help='Update Multiple Mobile Asset Tags with a CSV file')
	parser_updatemobileassettagcsv.set_defaults(cmd='updatemobileassettagcsv')
	parser_updatemobileassettagcsv.add_argument('csvfile', help='CSV file with two columns, unique mobile device identifier and asset tag number')

	parser_updatemobiledeviceinventory = subparsers.add_parser('updatemobiledeviceinventory', help='Issue update mobile device inventory command to a single device')
	parser_updatemobiledeviceinventory.set_defaults(cmd='updatemobiledeviceinventory')
	parser_updatemobiledeviceinventory.add_argument('mobileSearch', help='Mobile Device to issue update inventory command to')

	# not ready yet
	#parser_updatemobiledevicename = subparsers.add_parser('updatemobiledevicename', help='Update Mobile Device Name (Supervised Devices only)')
	#parser_updatemobiledevicename.set_defaults(cmd='updatemobiledevicename')
	#parser_updatemobiledevicename.add_argument('mobileSearch', help='Mobile Device to update device name')
	#parser_updatemobiledevicename.add_argument('deviceName', help='Updated device name')

	parser_updatemobiledeviceuserinfo = subparsers.add_parser('updatemobiledeviceuserinfo', help='Update User and Location Info')
	parser_updatemobiledeviceuserinfo.set_defaults(cmd='updatemobiledeviceuserinfo')
	parser_updatemobiledeviceuserinfo.add_argument('mobileDeviceID', help='JSS Mobile Device ID')
	parser_updatemobiledeviceuserinfo.add_argument('-u', '--username', default='', help='Username')
	parser_updatemobiledeviceuserinfo.add_argument('-n', '--real_name', default='', help='Real Name')
	parser_updatemobiledeviceuserinfo.add_argument('-e', '--email_address', default='', help='Email Address')
	parser_updatemobiledeviceuserinfo.add_argument('-p', '--position', default='', help='Position')
	parser_updatemobiledeviceuserinfo.add_argument('-t', '--phone', default='', help='Phone Number')
	parser_updatemobiledeviceuserinfo.add_argument('-d', '--department', default='', help='Department')
	parser_updatemobiledeviceuserinfo.add_argument('-b', '--building', default='', help='Building')
	parser_updatemobiledeviceuserinfo.add_argument('-r', '--room', default='', help='Room')
	parser_updatemobiledeviceuserinfo.add_argument('-o', '--overwrite', default='n', help='Overwrite all existing values [y] or update only [n]. Default is no')
	parser_updatemobiledeviceuserinfofromcsv = subparsers.add_parser('updatemobiledeviceuserinfofromcsv', help='Update Mobile Device User and Location Info from JSS IDs in CSV file')
	parser_updatemobiledeviceuserinfofromcsv.set_defaults(cmd='updatemobiledeviceuserinfofromcsv')
	parser_updatemobiledeviceuserinfofromcsv.add_argument('csvfile', help='Full path to CSV File with 9 columns: JSS Mobile Device ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite')

	parser_wipemobiledevice = subparsers.add_parser('wipemobiledevice', help='Wipe a mobile device')
	parser_wipemobiledevice.set_defaults(cmd='wipemobiledevice')
	parser_wipemobiledevice.add_argument('mobileSearch', help='Mobile Device to wipe')
	parser_wipemobiledevice.add_argument('-f', '--force', default='no', help='Force wipe without confirmation')

	parser_wipemobiledevicescsv = subparsers.add_parser('wipemobiledevicescsv', help='Wipe multiple devices using a CSV file, will confirm before proceeding')
	parser_wipemobiledevicescsv.set_defaults(cmd='wipemobiledevicescsv')
	parser_wipemobiledevicescsv.add_argument('csvfile', help='Full path to CSV file with one column (including header row) with unique mobile devices to wipe')

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

	if APIcommand == 'addcomputertogroup':
		computerSearch = args.computerSearch
		computerGroupSearch = args.computerGroupSearch
		computer_core.addComputerToGroup(computerSearch, computerGroupSearch, user, password)
	elif APIcommand == 'addmobiledevicetogroup':
		mobileSearch = args.mobileSearch
		mobileGroupSearch = args.mobileGroupSearch
		mobiledevicegroups.addMobileDeviceToGroup(mobileSearch, mobileGroupSearch, user, password)
	elif APIcommand == 'clearmobiledevicepasscode':
		mobileSearch = args.mobileSearch
		mobiledevices.clearMobileDevicePasscode(mobileSearch, user, password)
	elif APIcommand == 'deletecomputerbyid':
		computerID = args.computerID
		computer_lifecycle.deleteComputerByID(computerID, user, password)
	elif APIcommand == 'deletecomputeridsfromcsv':
		computersCSV = args.csvfile
		computer_lifecycle.deleteComputerIDsFromCSV(computersCSV, user, password)
	elif APIcommand == 'deletemobiledevicebyid':
		mobiledeviceID = args.mobiledeviceID
		mobiledevice_lifecycle.deleteMobileDeviceByID(mobiledeviceID, user, password)
	elif APIcommand == 'findmobiledeviceid':
		searchString = args.searchString
		mobiledevice_core.findMobileDeviceId(searchString, user, password)
	elif APIcommand == 'getcomputer':
		compSearch = args.compsearch
		detail = args.detail
		computer_core.getComputer(compSearch, user, password, detail)
	elif APIcommand == 'getcomputerbyid':
		computerID = args.computerID
		computer_core.getComputerByID(computerID, user, password)
	elif APIcommand == 'getcomputergroupid':
		groupSearch = args.groupsearch
		computergroups.getComputerGroupId(groupSearch, user, password)
	elif APIcommand == 'getcomputerextensionattributes':
		computerID = args.computerID
		computer_ea.getCompEAsbyCompID(computerID, user, password)
	elif APIcommand == 'getcomputergroupmembers':
		groupSearch = args.groupsearch
		computergroups.getComputerGroupMembers(groupSearch, user, password)
	elif APIcommand == 'getmobiledevice':
		mobilesearch = args.mobilesearch
		detail = args.detail
		mobiledevice_core.getMobileDevice(mobilesearch, user, password, detail)
	elif APIcommand == 'getmobiledevicebyid':
		mobileDeviceID = args.mobileDeviceID
		mobiledevice_core.getMobileDeviceByID(mobileDeviceID, user, password)
	elif APIcommand == 'getmobiledevicegroup':
		mobileDeviceGroup = args.mobilegroupsearch
		mobiledevicegroups.getMobileDeviceGroup(mobileDeviceGroup, user, password)
	elif APIcommand == 'getmobiledevicescsv':
		mobileDevicesCSV = args.csvfile
		mobiledevice_core.printMobileDevicesCSV(mobileDevicesCSV, user, password)
	elif APIcommand == 'getallcomputergroups':
		computergroups.getAllComputerGroups(user, password)
	elif APIcommand == 'getallpolicies':
		policies_core.getAllPolicies(user, password)
	elif APIcommand == 'getpolicybyid':
		policyid = args.policyid
		policies_core.getPolicybyId(policyid, user, password)
	elif APIcommand == 'getenabledpolicies':
		policies_extended.getEnabledPolicies(user, password)
	elif APIcommand == 'getenabledpoliciestocsv':
		policies_extended.getEnabledPoliciestoCSV(user, password)
	elif APIcommand == 'getpoliciesscopedtogroup':
		groupid = args.groupid
		policies_extended.getPoliciesScopedtoGroup(groupid, user, password)
	elif APIcommand == 'lockmobiledevice':
		mobileSearch = args.mobileSearch
		mobiledevice_lifecycle.lockMobileDevice(mobileSearch, user, password)
	elif APIcommand == 'lockmobiledevicescsv':
		mobileDevicesCSV = args.csvfile
		mobiledevice_lifecycle.lockMobileDevicesCSV(mobileDevicesCSV, user, password)
	elif APIcommand == 'removecomputerfromgroup':
		computerSearch = args.computerSearch
		computerGroupSearch = args.computerGroupSearch
		computer_core.removeComputerFromGroup(computerSearch, computerGroupSearch, user, password)
	elif APIcommand == 'removemobiledevicefromgroup':
		mobileSearch = args.mobileSearch
		mobileGroupSearch = args.mobileGroupSearch
		mobiledevicegroups.removeMobileDeviceFromGroup(mobileSearch, mobileGroupSearch, user, password)
	elif APIcommand == "unmanagecomputer":
		computerID = args.computerID
		computer_lifecycle.unmanageComputer(computerID, user, password)
	elif APIcommand == 'unmanagecomputeridsfromcsv':
		computersCSV = args.csvfile
		computer_lifecycle.unmanageComputerIDsFromCSV(computersCSV, user, password)
	elif APIcommand == 'updateassettag':
		computerID = args.computerID
		assetTag = args.assetTag
		computer_core.updateAssetTag(computerID, assetTag, user, password)
	elif APIcommand == 'updatecomputeruserinfo':
		computerID = args.computerID
		username = args.username
		real_name = args.real_name
		email_address = args.email_address
		position = args.position
		phone = args.phone
		department = args.department
		building = args.building
		room = args.room
		overwrite = args.overwrite
		computer_core.updateComputerUserInfo(computerID, username, real_name, email_address, position, phone, department, building, room, overwrite, user, password)
	elif APIcommand == 'updatecomputeruserinfofromcsv':
		computersCSV = args.csvfile
		computer_core.updateComputerUserInfoFromCSV(computersCSV, user, password)
	elif APIcommand == 'updatemobileassettag':
		mobileSearch = args.mobileSearch
		assetTag = args.assetTag
		mobiledevices.updateMobileAssetTag(mobileSearch, assetTag, user, password)
	elif APIcommand == 'updatemobileassettagcsv':
		csvfile = args.csvfile
		mobiledevices.updateMobileAssetTagsCSV(csvfile, user, password)
	elif APIcommand == 'updatemobiledevicename':
		mobileSearch = args.mobileSearch
		deviceName = args.deviceName
		mobiledevices.updateMobileDeviceName(mobileSearch, deviceName, user, password)
	elif APIcommand == 'updatemobiledeviceuserinfo':
		mobileDeviceID = args.mobileDeviceID
		username = args.username
		real_name = args.real_name
		email_address = args.email_address
		position = args.position
		phone = args.phone
		department = args.department
		building = args.building
		room = args.room
		overwrite = args.overwrite
		mobiledevices.updateMobileDeviceUserInfo(mobileDeviceID, username, real_name, email_address, position, phone, department, building, room, overwrite, user, password)
	elif APIcommand == 'updatemobiledeviceuserinfofromcsv':
		mobileDevicesCSV = args.csvfile
		mobiledevices.updateMobileDeviceUserInfoFromCSV(mobileDevicesCSV, user, password)
	elif APIcommand == 'updatemobiledeviceinventory':
		mobileSearch = args.mobileSearch
		mobiledevices.updateMobileDeviceInventory(mobileSearch, user, password)
	elif APIcommand == 'wipemobiledevice':
		mobileSearch = args.mobileSearch
		force = args.force
		mobiledevice_lifecycle.wipeMobileDevice(mobileSearch, user, password, force)
	elif APIcommand == 'wipemobiledevicescsv':
		mobileDevicesCSV = args.csvfile
		mobiledevice_lifecycle.wipeMobileDevicesCSV(mobileDevicesCSV, user, password)
	else:
		print 'Unknown command.'

if __name__ == '__main__':
	## Set the JSS API URL
	jss_api_base_url = getJSS_API_URL()

	## Run the main parser and command line interface
	main()
