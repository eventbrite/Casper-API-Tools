import sys
sys.path.append('..')
import csv
from csv import writer, DictWriter
from utilities import jamfconfig
from utilities import apirequests
import mobiledevice_core
import xml.etree.ElementTree as etree
import urllib2

jss_api_base_url = jamfconfig.getJSS_API_URL()


def clearMobileDevicePasscode(mobileSearch, username, password):
    print 'Issuing Clear Passcode command for mobile device ' + mobileSearch + ' ...'
    mobile_id = mobiledevice_core.getMobileDeviceId(mobileSearch, username, password)
    if str(mobile_id) == '-1':
        print 'Mobile device ' + mobileSearch + ' not found, please try again.'
        return -1
    elif str(mobile_id) == '-2':
        print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
        return -1

    postStr = jss_api_base_url + '/mobiledevicecommands/command/ClearPasscode'

    postXML = "<mobile_device_command><command>ClearPasscode</command><mobile_devices><mobile_device><id>" + mobile_id + "</id></mobile_device></mobile_devices></mobile_device_command>"

    response = apirequests.sendAPIRequest(postStr, username, password, 'POST', postXML)

    if response == -1:
        print 'Failed to issued clear passcode command for device ' + mobileSearch
        return -1
    else:
        print 'Successfully issued clear passcode command for device ' + mobileSearch
        return 1


def updateMobileAssetTag(mobileSearch, asset_tag, username, password):
    print "Running refactored updateMobileAssetTag...\n"
    print 'Updating asset tag for mobile device ' + mobileSearch + ' with asset tag ' + asset_tag + '...'
    mobile_id = mobiledevice_core.getMobileDeviceId(mobileSearch, username, password)
    if str(mobile_id) == '-1':
        print 'Mobile device ' + mobileSearch + ' not found, please try again.'
        return
    elif str(mobile_id) == '-2':
        print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
        return

    putStr = jss_api_base_url + '/mobiledevices/id/' + mobile_id
    #print putStr

    putXML = "<mobile_device><general><asset_tag>" + asset_tag + "</asset_tag></general></mobile_device>"
    response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

    if response == -1:
        print 'Failed to update asset tag for mobile device ' + mobileSearch + ', see error above.'
        return
    else:
        print 'Successfully updated asset tag for mobile device ' + mobileSearch + '.'


def updateMobileAssetTagsCSV(mobileAssetTagsCSV, username, password):
    print "Running refactored updateMobileAssetTagsCSV...\n"

    # CSV file with two columns (with headers), first column = unique mobile search string (typically serial number), second column = asset tag

    with open (mobileAssetTagsCSV, 'rU') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        #Skip the header row
        next(csvreader, None)

        for row in csvreader:
            mobileSearch = row[0].replace('"', '').strip()
            mobileAssetTag = row[1].replace('"', '').strip()
            #print 'Test Run: Update mobile asset ' + mobileSearch + ' with asset tag ' + mobileAssetTag
            updateMobileAssetTag(mobileSearch, mobileAssetTag, username, password)


def updateMobileDeviceInventory(mobileSearch, username, password):
    print "Running refactored updateMobileDeviceInventory...\n"
    print 'Issuing Update Inventory command for mobile device ' + mobileSearch + ' ...'
    mobile_id = mobiledevice_core.getMobileDeviceId(mobileSearch, username, password)
    if str(mobile_id) == '-1':
        print 'Mobile device ' + mobileSearch + ' not found, please try again.'
        return -1
    elif str(mobile_id) == '-2':
        print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
        return -1

    #postStr = jss_api_base_url + '/mobiledevicecommands/command/UpdateInventory/id/' + mobile_id
    postStr = jss_api_base_url + '/mobiledevicecommands/command/UpdateInventory'

    postXML = "<mobile_device_command><command>UpdateInventory</command><mobile_devices><mobile_device><id>" + mobile_id + "</id></mobile_device></mobile_devices></mobile_device_command>"
    #print postStr
    #print postXML
    #return

    response = apirequests.sendAPIRequest(postStr, username, password, 'POST', postXML)

    if response == -1:
        print 'Failed to issued update inventory command for device ' + mobileSearch
        return -1
    else:
        print 'Successfully issued update inventory command for device ' + mobileSearch
        return 1


def updateMobileDeviceName(mobileSearch, deviceName, username, password):
    print "Running refactored updateMobileDeviceName...\n"
    print 'Updating Mobile Device name for mobile device ' + mobileSearch + ' to ' + deviceName + '...'
    newDeviceName_normalized = urllib2.quote(deviceName)

    mobile_id = mobiledevice_core.getSupervisedMobileDeviceId(mobileSearch, username, password)
    if str(mobile_id) == '-1':
        print 'Mobile device ' + mobileSearch + ' not found, please try again.'
        return -1
    elif str(mobile_id) == '-2':
        print 'More than one mobile device matching search string ' + str(mobileSearch) + ', please try again.'
        return -1
    elif str(mobile_id) == '-3':
        print 'Device found, but is not supervised.'

    postStr = jss_api_base_url + '/mobiledevicecommands/command/DeviceName/' + newDeviceName_normalized + '/id/' + mobile_id
    postXML = "<mobile_device_command><command>DeviceName</command><mobile_devices><mobile_device><id>" + mobile_id + "</id><device_name>" + deviceName + "</device_name></mobile_device></mobile_devices></mobile_device_command>"


def updateMobileDeviceUserInfo(mobile_id, username, real_name, email_address, position, phone, department, building, room, overwrite, jssuser, jsspassword):
    print "Running refactored updateMobileDeviceUserInfo...\n"


    putStr = jss_api_base_url + '/mobiledevices/id/' + mobile_id
    if overwrite == 'y':
        print 'Overwriting all existing user and location info for mobile device ID ' + mobile_id + ' with the following:\n' + '\n  Username: ' + username + '\n  Full Name: ' + real_name + '\n  Email: ' + email_address + '\n  Position: ' + position + '\n  Phone: ' + str(phone) + '\n  Department: ' + department + '\n  Building: ' + building + '\n  Room: ' + room + '\n'
        putXML = "<mobile_device><location><username>" + username + "</username><real_name>" + real_name + "</real_name><email_address>" + email_address + "</email_address><position>" + position + "</position><phone>" + str(phone) + "</phone><department>" + department + "</department><building>" + building + "</building><room>" + room + "</room></location></mobile_device>"
    else:
        updateStr = 'Updating user and location info for mobile device id ID ' + mobile_id + ' with the following:\n'
        putXML = "<mobile_device><location>"
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

        putXML += "</location></mobile_device>"

        if updateCount == 0:
            # Nothing to update
            print "Nothing to update."
            return


    #print putXML
    response = apirequests.sendAPIRequest(putStr, jssuser, jsspassword, 'PUT', putXML)

    if response == -1:
        print 'Failed to update user and location info for mobile device ' + mobile_id + ', see error above.'
        return
    else:
        print 'Successfully updated user and location info for mobile device ' + mobile_id + '.'



def updateMobileDeviceUserInfoFromCSV(mobiledevicesCSV, username, password):
    print "Running refactored updateMobileDeviceUserInfoFromCSV...\n"

    # CSV File with 9 columns: JSS Mobile Device ID, Username, Full Name, Email, Position, Phone, Department, Building, Room, Overwrite

    with open (mobiledevicesCSV, 'rU') as csvfile:
        mobiledevicesreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        #Skip the header row
        next(mobiledevicesreader, None)

        for row in mobiledevicesreader:
            mobileDeviceID = row[0].replace('"', '').strip()
            uName = row[1].replace('"', '').strip()
            fullName = row[2].replace('"', '').strip()
            email = row[3].replace('"', '').strip()
            position = row[4].replace('"', '').strip()
            phone = row[5].replace('"', '').strip()
            department = row[6].replace('"', '').strip()
            building = row[7].replace('"', '').strip()
            room = row[8].replace('"', '').strip()
            overwrite = row[9].replace('"', '').strip()

            print 'Update mobile device user info with ' + 'JSS ID: ' + mobileDeviceID + ' Username: ' + uName + ' Full Name: ' + fullName + ' Email: ' + email + ' Position: ' + position + ' Phone: ' + str(phone) + ' Dept: ' + department + 'Bldg: ' + building + ' Room: ' + room + ' Overwrite: ' + overwrite
            updateMobileDeviceUserInfo(mobileDeviceID, uName, fullName, email, position, phone, department, building, room, overwrite, username, password)
    return
