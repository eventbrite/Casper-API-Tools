import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree
import csv
from csv import writer, DictWriter

import mobiledevices
import mobiledevice_core

jss_api_base_url = jamfconfig.getJSS_API_URL()

def deleteMobileDeviceByID(mobile_id, username, password):
	print "Running refactored deleteMobileDeviceByID...\n"

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


def deleteMobileIDsFromCSV(mobilesCSV, username, password):
    print 'Running refactored deleteMobileIDsFromCSV...\n'

    # CSV file with one column, just JSS computer IDs

    with open (mobilesCSV, 'rU') as csvfile:
        mobilereader = csv.reader(csvfile, delimiter=',', quotechar='|')

        #Skip the header row
        next(mobilereader, None)

        for row in mobilereader:
            mobile_ID = row[0].replace('"', '').strip()
            print 'Test Run: Delete MobileDevice ID ' + mobile_ID
            deleteMobileDeviceByID(mobile_ID, username, password)


def lockMobileDevice(mobileSearch, username, password):
	print "Running refactored lockMobileDevice...\n"

	try:
		print 'Searching for mobile device ' + mobileSearch + '...'
		mobile_id = mobiledevice_core.getMobileDeviceId(mobileSearch, username, password)
		if str(mobile_id) == '-1':
			print 'Mobile device ' + mobileSearch + ' not found, please try again.'
			return -1
		elif str(mobile_id) == '-2':
			print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
			return -1


		postStr = jss_api_base_url + '/mobiledevicecommands/command/DeviceLock'
		postXML = "<mobile_device_command><command>DeviceLock</command><mobile_devices><mobile_device><id>" + mobile_id + "</id></mobile_device></mobile_devices></mobile_device_command>"
		#print postStr
		#print postXML
		#return

		mobiledevice_core.getMobileDeviceByID(mobile_id, username, password)

		usrInput = raw_input('\nAre you sure you want to lock the mobile device listed above? [y/n]: ')
		if usrInput == 'y':
			print 'Issuing remote lock command...'
			#return 1
			response = apirequests.sendAPIRequest(postStr, username, password, 'POST', postXML)

			if response == -1:
				print 'Failed to issue lock command for device ' + mobileSearch
				return -1
			else:
				print 'Successfully issued lock command for device ' + mobileSearch
				return 1
		else:
			print 'Aborting request to lock mobile device...'
			return -1

	except TypeError as error:
		print 'There was a problem getting device details, unable to issue lock command. \nCheck for irregular characters in the Device name.'
		continueInput = raw_input('\nPress ENTER to continue...')
		if continueInput != '':
			return




def lockMobileDevicesCSV(devicesCSV, username, password):
	print "Running refactored lockMobileDevicesCSV...\n"
	devicesDict = mobiledevice_core.getMobileDevicesCSV(devicesCSV, username, password)

	for (device, info) in devicesDict.items():
		#print "%s, %s" % (device, ', '.join(info))
		print "Sending lock device command for device %s with JSS id %s" % (device, info[2])
		lockMobileDevice(device, username, password)


# Wipe Mobile Device with no confirmation, using mobile device jss id
def wipeMobileDeviceNoConfirm(mobile_id, username, password):
	print "Running refactored wipeMobileDeviceNoConfirm...\n"
	postStr = jss_api_base_url + '/mobiledevicecommands/command/EraseDevice'

	postXML = "<mobile_device_command><command>EraseDevice</command><mobile_devices><mobile_device><id>" + mobile_id + "</id></mobile_device></mobile_devices></mobile_device_command>"
	print 'Issuing erase device command for mobile device id ' + mobile_id + ' ...'
	response = apirequests.sendAPIRequest(postStr, username, password, 'POST', postXML)


def wipeMobileDevicesCSV(devicesCSV, username, password):
	print "Running refactored wipeMobileDevicesCSV...\n"
	devicesDict = mobiledevice_core.getMobileDevicesCSV(devicesCSV, username, password)

	if len(devicesDict) == 0:
		print 'No devices found to wipe, aborting...'
		return -1
	## Print confirmation message

	print '\nDevice Name\tSerial Number\tAsset\tJSS ID'
	print '===========\t=============\t=====\t======'
	for (device, info) in devicesDict.items():
		print "%s\t%s" % (device, '\t'.join(info))

	sure = raw_input('\nAre you sure you want to send wipe commands to the above mobile devices? (y/n): ')

	if sure == 'y':
		for (device, info) in devicesDict.items():
			#print "%s, %s" % (device, ', '.join(info))
			jss_id = info[2]
			print "Sending wipe device command for device %s with JSS id %s" % (device, jss_id)
			wipeMobileDeviceNoConfirm(jss_id, username, password)
	else:
		print 'Aborting request to wipe mobile devices...'


def wipeMobileDevice(mobileSearch, username, password, force):
	print "Running refactored wipeMobileDevice...\n"

	try:

		print 'Mobile Device wipe requested, getting information for mobile device ' + mobileSearch + ' ...'

		mobile_id = mobiledevice_core.getMobileDeviceId(mobileSearch, username, password)
		if str(mobile_id) == '-1':
			print 'Mobile device ' + mobileSearch + ' not found, please try again.'
			return -1
		elif str(mobile_id) == '-2':
			print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
			return -1

		if force == 'yes':
			print "Wiping device %s without confirmation" % mobile_id
			#return
			wipeMobileDeviceNoConfirm(mobile_id, username, password)
		else:

			postStr = jss_api_base_url + '/mobiledevicecommands/command/EraseDevice'

			postXML = "<mobile_device_command><command>EraseDevice</command><mobile_devices><mobile_device><id>" + mobile_id + "</id></mobile_device></mobile_devices></mobile_device_command>"

			mobiledevice_core.getMobileDeviceByID(mobile_id, username, password)

			usrInput = raw_input('\nAre you sure you want to wipe the mobile device listed above? [y/n]: ')

			if usrInput == 'y':
				print 'Issuing erase device command for mobile device ' + mobileSearch + ' ...'
				#return 1
				response = apirequests.sendAPIRequest(postStr, username, password, 'POST', postXML)

				if response == -1:
					print 'Failed to issue wipe command for device ' + mobileSearch
					return -1
				else:
					print 'Successfully issued wipe command for device ' + mobileSearch
					return 1
			else:
				print 'Aborting request to wipe mobile device...'
				return -1

	except TypeError as error:
		print 'There was a problem getting device details, unable to issue wipe command. \nCheck for irregular characters in the Device name.'
		continueInput = raw_input('\nPress ENTER to continue...')
		if continueInput != '':
			return

