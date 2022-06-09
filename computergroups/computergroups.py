import sys
sys.path.append('..')
import urllib2
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()
#print("JSS API Base URL: {}".format(jss_api_base_url))

def cleanupOutput(inputString):
    #print str(inputString)
    return inputString.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", "\"").replace(u"\u201d", "\"")

def getAllComputerGroups(username, password):
    ''' Lists all computer groups in JSS to screen, returning ID, name, and type '''
    print 'Running refactored getAllComputerGroups...\n'

    print "Getting All JAMF Computer Groups...\n"
    reqStr = jss_api_base_url + '/computergroups'

    r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

    if r == -1:
        return

    baseXml = r.read()
    responseXml = etree.fromstring(baseXml)
    groupCount = 0
    smartCount = 0
    staticCount = 0

    for group in responseXml.findall('computer_group'):
        groupCount += 1
        groupID = group.find('id').text
        groupName = group.find('name').text

        if group.find('is_smart').text == 'true':
            groupType = 'Smart'
            smartCount += 1
        else:
            groupType = 'Static'
            staticCount += 1

        print 'Group ID: ' + groupID + ', ' + 'Group Name: ' + groupName + 'Group Type: ' + groupType + '\n'

    print '\nThere are {} total Computer Groups in the JSS'.format(groupCount)
    print '\nThere are {} Smart Groups, and {} Static Groups\n'.format(smartCount, staticCount)


def getComputerGroupId(groupSearch, username, password):
    print 'Running refactored getComputerGroupId...\n'
    groupSearch_normalized = urllib2.quote(groupSearch)

    reqStr = jss_api_base_url + '/computergroups/name/' + groupSearch_normalized

    r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

    if r != -1:
        responseCode = r.code
        #print 'Response Code: ' + str(responseCode)

        baseXml = r.read()
        responseXml = etree.fromstring(baseXml)

        computerGroupId = responseXml.find('id').text

        print 'Computer Group ID for "{}" is:  {}\n'.format(groupSearch, computerGroupId)
        return computerGroupId
    else:
        #print 'Group not found.'
        return -1


def getComputerGroupMembers(groupSearch, username, password):
    print 'Running refactored getComputerGroupMembers...\n'
    print 'Printing CSV of all members of the group matching ' + groupSearch + '...'
    # Find computer group JSS ID
    computer_group_id = getComputerGroupId(groupSearch, username, password)
    if str(computer_group_id) == '-1':
        print 'Computer group ' + groupSearch + ' not found, please try again.'
        return

    reqStr = jss_api_base_url + '/computergroups/id/' + str(computer_group_id)

    try:
        r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')
        #responseCode = str(r.code)

        #if '200' in str(responseCode):
        if r != -1:
            xmlstring = r.read()
            #print str(xmlstring)

            xml = etree.fromstring(xmlstring)
            #print prettify(xml)

            computers = xml.find('computers')
            members = []

            ## Add Header Row for CSV
            headerRow = "Computer Name, JSS ID, Serial Number"
            members += [ headerRow ]

            for computer in computers.findall('computer'):
                #print str(computer)
                comp_id = computer.find('id').text
                name = computer.find('name').text
                serial_number = computer.find('serial_number').text
                #print str(comp_id)
                #computerInfo = str(name)
                #email_address = getUserEmailByComputerID(comp_id, username, password)
                computerInfo = str(name) + ', ' + str(comp_id) + ', ' + str(serial_number)
                computerInfo = cleanupOutput(computerInfo)
                #print computerInfo.encode('ascii', 'ignore')
                members += [ computerInfo ]

            print '\n'.join (sorted(members))
            print 'Total Computers: ' + str(len(members)-1)

        elif '401' in str(responseCode):
            print "Authorization failed"
    except urllib2.HTTPError, err:
        if '401' in str(err):
            print 'Authorization failed, goodbye.'
