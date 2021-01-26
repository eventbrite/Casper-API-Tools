import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
from policies import policies_core

import csv
from csv import writer, DictWriter
import xml.etree.ElementTree as etree


jss_api_base_url = jamfconfig.getJSS_API_URL()
#print("JSS API Base URL: {}".format(jss_api_base_url))


def cleanupOutput(inputString):
	#print str(inputString)
	return inputString.replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u201c", "\"").replace(u"\u201d", "\"")


def getEnabledPolicies(username, password):
	''' Function to get all policies and filter out only currently enabled policies '''
	print 'Running refactored getenabledpolicies ...'

	## List for holding all policies / Empty list for results
	AllPolicies = policies_core.listAllPolicyIds(username, password)
	EnabledPolicies = []

	print '\nAbout to find all Enabled policies.  This may take some time...\n\n'

	print 'There are a total of {} policies...\n'.format(len(AllPolicies))

	for n in AllPolicies:
		thisPolicy = policies_core.listPolicybyId(n, username, password)
		if thisPolicy["Policy Enabled"] == 'true':
			EnabledPolicies.append({ "Policy ID": thisPolicy["Policy ID"], "Policy Name": thisPolicy["Policy Name"]})
			print '{} is an enabled policy'.format(thisPolicy["Policy Name"])


	print '\nTotal policies in JSS:  {}'.format(len(AllPolicies))
	print '\nTotal enabled policies:  {}'.format(len(EnabledPolicies))

	print '\nThe following policies are currently enabled: \n'

	for pol in EnabledPolicies:
		print pol


def getEnabledPoliciestoCSV(username, password):
	''' get Enabled Policies and export to CSV, along with scope and package info '''
	print 'Running refactored getenabledpoliciestoCSV ...'

	## List for holding all policies / Empty list for results
	AllPolicies = policies_core.listAllPolicyIds(username, password)
	EnabledPolicies = []

	csvOutPutFile = raw_input("\nEnter file name for desired CSV:  ")

	print '\nAbout to find all Enabled policies.  Grab a coffee.  This may take some time...\n\n'

	## iterate over AllPolicies dict
	## add to "EnabledPolicies" list if status ('enabled') evaluates true

	with open(csvOutPutFile, "a") as file:
		headers = ["Policy Name", "Policy ID", "Policy Enabled", "Policy Trigger", "Policy Frequency", "All Computers in Scope", "Scoped Computers", "Scoped Computer Groups", "Package Configuration"]
		csv_writer = DictWriter(file, fieldnames=headers)
		csv_writer.writeheader()

		for n in AllPolicies:
			thisPolicy = policies_core.listPolicybyId(n, username, password)
			if thisPolicy["Policy Enabled"] == 'true':
				csv_writer.writerow({
					"Policy ID": thisPolicy["Policy ID"],
					"Policy Name": thisPolicy["Policy Name"],
					"Policy Enabled": thisPolicy["Policy Enabled"],
					"Policy Trigger": thisPolicy["Policy Trigger"],
					"Policy Frequency": thisPolicy["Policy Frequency"],
					"All Computers in Scope": thisPolicy["All Computers in Scope"],
					"Scoped Computers": thisPolicy["Scoped Computers"],
					"Scoped Computer Groups": thisPolicy["Scoped Computer Groups"],
					"Package Configuration": thisPolicy["Package Configuration"]
					})
				print '{} is an enabled policy'.format(thisPolicy["Policy Name"])
				EnabledPolicies.append(thisPolicy["Policy Name"])

	print '\nResults are now available in ' + csvOutPutFile


def getPoliciesScopedtoGroup(groupid, username, password):
	''' Function to look up all enabled policies scoped to a user-specified group.
	Function iterate '''
	print 'Running refactored getpoliciesscopedtogroup ...'

	## List variables for holding all policies, enabled policies, scope data, and final results
	AllPolicyIDs = policies_core.listAllPolicyIds(username, password)
	scopeDetails = []
	groupScopeDetails = []

	print '\nSorting ALL THOSE policies. This may take quite a while...\n\n'

	print 'There are currently {} policies in the JSS\n'.format(len(AllPolicyIDs))

	# get all enabled policies' scope information as dict, save to list
	for polID in AllPolicyIDs:
		scopeDetails.append(policies_core.listPolicyScopebyId(polID, username, password))
		print 'Evaluating policy {} for scope details...'.format(polID)

	# iterate over Dict - if Groups in dict matches groupid, add to 'groupScopeDetails' list
	for p in scopeDetails:
		pData = {}
		groupIDlist = p["Computer group IDs: "]
		if groupid in groupIDlist:
			pData = { "Policy ID": p["Policy ID: "], "Policy Name": policies_core.listPolicyNamebyId(p["Policy ID: "], username, password) }
			groupScopeDetails.append(pData)

	if groupScopeDetails:
		print '\nTHE FOLLOWING POLICIES ARE SCOPED TO GROUP ID {}: \n'.format(groupid)
		for s in groupScopeDetails:
			print '\nPolicy ID: ' + s["Policy ID"]
			print 'Policy Name: ' + s["Policy Name"] + '\n'

	else:
		print '\nNo policies were found scoped to Group {}'.format(groupid)
		return


def deletePolicyByID(policy_id, username, password):
	print "Running refactored deletePolicyByID...\n"

	policies_core.getPolicybyId(policy_id, username, password)

	# Comment out raw input to remove deletion confirmations
	sure = raw_input('Are you sure you want to delete the policy above from the JSS? (y/n): ')

	if sure == 'y':
		print "Deleting Policy " + policy_id + "..."

	delStr = jss_api_base_url + '/policies/id/' + policy_id
	#print delStr
	response = apirequests.sendAPIRequest(delStr, username, password, 'DELETE')

	if response == -1:
		print 'Failed to delete policy. See errors above.'
	else:
		print 'Successfully deleted policy ' + policy_id

	# else:
	#   print 'Aborting request to delete mobile device ' + mobile_id

		## Uncomment this part to see the xml response
		#xmlstring = response.read()
		#xml = etree.fromstring(xmlstring)
		#print prettify(xml)

		#responseCode = str(response.code)
		#print 'Response Code: ' + responseCode


def deletePolicyIDsFromCSV(policiesCSV, username, password):
	print 'Running refactored deletePolicyIDsFromCSV...\n'

	# CSV file with one column, just JSS computer IDs

	with open (policiesCSV, 'rU') as csvfile:
		policyreader = csv.reader(csvfile, delimiter=',', quotechar='|')

		#Skip the header row
		next(policyreader, None)

		for row in policyreader:
			policy_ID = row[0].replace('"', '').strip()
			print 'Test Run: Delete Policy ID ' + policy_ID
			deletePolicyByID(policy_ID, username, password)
