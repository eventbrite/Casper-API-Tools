import sys
sys.path.append('..')
import urllib2
import csv
from csv import writer, DictWriter
from utilities import jamfconfig
from utilities import apirequests
import computer_core
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()

def getCompEAsbyCompID(compID, username, password):
    ''' List all Extension Attributes for computer in JSS to screen -
    including Extension Attribute's ID value for reference and additional lookup '''

    print "We're Refactored!  Getting All Computer Extension Attributes..."
    reqStr = jss_api_base_url + '/computers/id/' + compID

    r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

    if r == -1:
        return

    baseXml = r.read()
    responseXml = etree.fromstring(baseXml)
    extension_attributes = responseXml.find('extension_attributes')
    eas = []

    print '\nEXTENSION ATTRIBUTES:'

    for ea in extension_attributes.findall('extension_attribute'):
        eaID = ea.find('id').text
        eaName = ea.find('name').text
        eaValue = ea.find('value').text
        eaInfo = '(EA ID:  ' + str(eaID) + ') --- ' + str(eaName) + ': ' + str(eaValue)
        eas += [ eaInfo ]

    print '\n'.join (sorted (eas))


def getCompEAbyEAID(compID, extattribID, username, password):
    ''' Returns specific details for an Extension Attribute based upon that computer's
    JSS ID and the EA's JSS ID as arguments '''

    print "Running Refactored getCompEAbyEAID...\n"
    reqStr = jss_api_base_url + '/computers/id/' + compID

    r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

    if r == -1:
        return

    baseXml = r.read()
    responseXml = etree.fromstring(baseXml)
    extension_attributes = responseXml.find('extension_attributes')

    for ea in extension_attributes.findall('extension_attribute'):
        eaID = ea.find('id').text
        eaName = ea.find('name').text
        eaValue = ea.find('value').text
        # print eaID
        if eaID == extattribID:
            eaInfo = 'EA ID:  ' + str(eaID) + ' --- ' + str(eaName) + ': ' + str(eaValue)
            print eaInfo + '\n'
            return eaInfo

    print 'Extension Attribute with ID: {} not found in JSS.  Check the Extension Attribute ID again.\n'.format(extattribID)


def getCompEAbyEAname(compID, searchStr, username, password):
    ''' Returns specific details for an Extension Attribute based upon that computer's
    JSS ID and the EA's JSS ID as arguments '''

    print "Running Refactored getCompEAbyEAID...\n"
    reqStr = jss_api_base_url + '/computers/id/' + compID

    r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

    if r == -1:
        return

    baseXml = r.read()
    responseXml = etree.fromstring(baseXml)
    extension_attributes = responseXml.find('extension_attributes')
    eaInfo = []

    for ea in extension_attributes.findall('extension_attribute'):
        eaID = ea.find('id').text
        eaName = ea.find('name').text
        eaValue = ea.find('value').text
        # print eaName
        if searchStr in eaName:
            eaInfo.append('EA ID: ' + str(eaID) + ' --- ' + str(eaName) + ': ' + str(eaValue))

    if eaInfo:
        print '\n\n'.join (sorted (eaInfo))
    else:
        print 'No Extension Attribute was found containing: {}.  Try using another search string instead.\n'.format(searchStr)




