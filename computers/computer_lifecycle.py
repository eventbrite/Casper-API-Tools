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


def unmanageComputer(comp_id, username, password):
    print 'Running refactored unmanageComputer...\n'
    print "Unmanaging computer " + comp_id + "..."

    #reqStr = jss_api_base_url + '/computercommands/command/UnmanageDevice'
    #print reqStr

    putStr = jss_api_base_url + '/computers/id/' + comp_id
    #print putStr

    #postXML = "<computers><computer><general><id>" + comp_id + "</id><remote_management><managed>false</managed></remote_management></general></computer></computers>"

    putXML = "<computer><general><remote_management><managed>false</managed></remote_management></general></computer>"
    response = apirequests.sendAPIRequest(putStr, username, password, 'PUT', putXML)

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


def unmanageComputerIDsFromCSV(computersCSV, username, password):
    print 'Running refactored unmanageComputerIDsFromCSV...\n'

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
    print 'Running refactored deleteComputerByID...\n'

    computer_core.getComputerByIDShort(comp_id, username, password)

    sure = raw_input('Are you sure you want to delete the computer above from the JSS? (y/n): ')

    if sure == 'y':
        print "Deleting computer " + comp_id + "..."

        delStr = jss_api_base_url + '/computers/id/' + comp_id
        #print delStr
        response = apirequests.sendAPIRequest(delStr, username, password, 'DELETE')

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


def deleteComputerByIDBulk(comp_id, username, password):
    ''' Same as deleteComputerbyID function with added error logging for playback '''

    compDict = computer_core.getComputerByIDShort(comp_id, username, password)

    # sure = raw_input('Are you sure you want to delete the computer above from the JSS? (y/n): ')

    # if sure == 'y':
    print "Deleting computer " + comp_id + "..."

    delStr = jss_api_base_url + '/computers/id/' + comp_id
        #print delStr
    response = apirequests.sendAPIRequest(delStr, username, password, 'DELETE')

    if response == -1:
        print 'Failed to delete computer. See errors above.'
        return compDict
    else:
        print 'Successfully deleted computer ' + comp_id

    # else:
    #     print 'Aborting request to delete computer ' + comp_id


def deleteComputerIDsFromCSV(computersCSV, username, password):
    print 'Running refactored deleteComputerIDsFromCSV...\n'

    errList = []
    successList = []

    # CSV file with one column, just JSS computer IDs

    with open (computersCSV, 'rU') as csvfile:
        computerreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        #Skip the header row
        next(computerreader, None)

        for row in computerreader:
            compID = row[0].replace('"', '').strip()
            # print 'Test Run: Delete computer ID ' + compID

            # deletComputerByIDBulk function returns a comp details dict if errors
            delResult = deleteComputerByIDBulk(compID, username, password)
            if delResult:
                print 'Encountered a problem deleting computer ID:  ' + compID + '\n'
                errList.append(delResult)

    if errList:
        print '\nERROR SUMMARY:\n'
        print 'The Following Computers Encountered Errors During Deletion:  \n'
        for compDict in errList:
            print compDict
        print '\n\n'
    else:
        print 'Finished Deleting Jamf Computer Records.  Have a nice day! \n'





