import sys
sys.path.append('..')
import urllib2
import csv
from csv import writer, DictWriter
from utilities import jamfconfig
from utilities import apirequests
import computer_core
from computergroups import computergroups
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()

def getCompEAsbyCompID(compID, username, password):
    ''' List all Extension Attributes for computer in JSS to screen '''

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
        eaName = ea.find('name').text
        eaValue = ea.find('value').text
        eaPair = str(eaName) + ': ' + str(eaValue)
        eas += [ eaPair ]

    print '\n'.join (sorted (eas))

