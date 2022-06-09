import sys
sys.path.append('..')
import urllib2
import csv
from csv import writer, DictWriter
from utilities import jamfconfig
from utilities import apirequests
import mobiledevice_core
import mobiledevices
import xml.etree.ElementTree as etree
import urllib2

jss_api_base_url = jamfconfig.getJSS_API_URL()

def getMobileDeviceGroup(mobile_device_group_name, username, password):
    print "Running refactored getMobileDeviceGroup...\n"
    print 'Getting mobile device group named: ' + mobile_device_group_name + '...'
    mobile_device_group_name_normalized = urllib2.quote(mobile_device_group_name)

    reqStr = jss_api_base_url + '/mobiledevicegroups/name/' + mobile_device_group_name_normalized


    #print reqStr

    r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

    if r != -1:
        responseCode = r.code

        #print 'Response Code: ' + str(responseCode)

        baseXml = r.read()
        responseXml = etree.fromstring(baseXml)

        mobileDeviceGroupId = responseXml.find('id').text
        mobileDeviceGroupSize = responseXml.find('mobile_devices/size').text

        #print prettify(responseXml)

        if str(mobileDeviceGroupSize) == '0':
            print 'No devices in this group'
            return mobileDeviceGroupId

        print 'Group ID: ' + mobileDeviceGroupId
        #print prettify(responseXml)
        mobiledevicemembers = responseXml.find('mobile_devices')

        mobiledevices = []
        for mobiledevice in mobiledevicemembers.findall('mobile_device'):
            mobiledevicename = mobiledevice.find('name').text
            mobiledeviceid = mobiledevice.find('id').text
            mobiledeviceserial = mobiledevice.find('serial_number').text
            mobiledeviceinfo = str(mobiledevicename) + ', ' + str(mobiledeviceid) + ', ' + str(mobiledeviceserial)
            mobiledevices += [ mobiledeviceinfo ]
        print 'All devices in group ' + mobile_device_group_name + ' [name, jss_id, serial_no]:\n'
        print '\n'.join (sorted (mobiledevices))
        print '\nTotal Devices: ' + str(len(mobiledevices))
        return mobileDeviceGroupId
    else:
        print 'Failed to find mobile device group with name ' + mobile_device_group_name
        return -1

def addMobileDeviceToGroup(mobile_device, mobile_device_group, username, password):
    print "Running refactored addMobileDeviceToGroup...\n"
    # Find mobile device JSS ID
    mobile_device_id = mobiledevice_core.getMobileDeviceId(mobile_device, username, password)
    if str(mobile_device_id) == '-1':
        print 'Mobile device ' + mobile_device + ' not found, please try again.'
        return
    elif str(mobile_device_id) == '-2':
        print 'More than one mobile device found matching search string ' + mobile_device + ', please try again.'
        return

    # Find mobile device group ID
    mobile_device_group_id = getMobileDeviceGroup(mobile_device_group, username, password)
    if str(mobile_device_group_id) == '-1':
        print 'Mobile device group ' + mobile_device_group + ' not found, please try again.'
        return

    print 'Adding mobile device id ' + str(mobile_device_id) + ' to group id ' + str(mobile_device_group_id)

    putStr = jss_api_base_url + '/mobiledevicegroups/id/' + str(mobile_device_group_id)
    putXML = '<mobile_device_group><mobile_device_additions><mobile_device><id>' + str(mobile_device_id) + '</id></mobile_device></mobile_device_additions></mobile_device_group>'

    #print putStr
    #print putXML
    #return

    response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

    if response == -1:
        print 'Failed to add mobile device ' + mobile_device + ' to group, see error above.'
        return
    else:
        print 'Successfully added mobile device ' + mobile_device + ' to group ' + mobile_device_group + '.'


def removeMobileDeviceFromGroup(mobile_device, mobile_device_group, username, password):
    print "Running refactored removeMobileDeviceFromGroup...\n"
    # Find mobile device JSS ID
    mobile_device_id = mobiledevice_core.getMobileDeviceId(mobile_device, username, password)
    if str(mobile_device_id) == '-1':
        print 'Mobile device ' + mobile_device + ' not found, please try again.'
        return
    elif str(mobile_device_id) == '-2':
        print 'More than one mobile device matching search string ' + mobile_device + ', please try again.'
        return

    # Find mobile device group ID
    mobile_device_group_id = getMobileDeviceGroup(mobile_device_group, username, password)
    if str(mobile_device_group_id) == '-1':
        print 'Mobile device group ' + mobile_device_group + ' not found, please try again.'
        return

    print 'Removing mobile device id ' + str(mobile_device_id) + ' from group id ' + str(mobile_device_group_id)

    putStr = jss_api_base_url + '/mobiledevicegroups/id/' + str(mobile_device_group_id)
    putXML = '<mobile_device_group><mobile_device_deletions><mobile_device><id>' + str(mobile_device_id) + '</id></mobile_device></mobile_device_deletions></mobile_device_group>'

    #print putStr
    #print putXML
    #return

    response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

    if response == -1:
        print 'Failed to remove mobile device ' + mobile_device + ' to group, see error above.'
        return
    else:
        print 'Successfully remove mobile device ' + mobile_device + ' to group ' + mobile_device_group + '.'
