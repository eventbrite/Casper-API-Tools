import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()
#print("JSS API Base URL: {}".format(jss_api_base_url))

def getAllPolicies(username, password):
	''' List all policies in JSS to screen '''
	#print(username)

	print "We're Refactored!  Getting All JAMF Policies..."
	reqStr = jss_api_base_url + '/policies'

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r == -1:
		return

	baseXml = r.read()
	responseXml = etree.fromstring(baseXml)

	for policy in responseXml.findall('policy'):
		policyName = policy.find('name').text
		policyID = policy.find('id').text

		print 'Policy ID: ' + policyID + ',  ' + 'Policy Name: ' + policyName + '\n'

def getPolicybyId(policyid, username, password):
	''' Method to search for Policy ID by ID number and return General Policy Information, Scoping Information, and Package Configuration information - send results to Stdout '''

	print 'Running refactored getpolicybyid ...'
	reqStr = jss_api_base_url + '/policies/id/' + policyid

	r = apirequests.sendAPIRequest(reqStr, username, password, 'GET')

	if r != -1:

		baseXml = r.read()
		responseXml = etree.fromstring(baseXml)

		general = responseXml.find('general')

		## General Policy Information
		name = general.find('name').text
		policy_id = general.find('id').text
		enabled = general.find('enabled').text
		trigger = general.find('trigger').text
		frequency = general.find('frequency').text

		print '\nGENERAL POLICY INFORMATION: '
		print 'Policy Name: ' + str(name)
		print 'Policy ID #: ' + str(policy_id)
		print 'Policy is Enabled: ' + str(enabled)
		print 'Policy Trigger: ' + str(trigger)
		print 'Policy Frequency: ' + str(frequency)

		## Policy Scope Information
		scope = responseXml.find('scope')
		allcomputers = scope.find('all_computers').text
		groups = scope.find('computer_groups')
		comp_groups = []
		computers = scope.find('computers')
		members = []

		## Add Header Row for output for info categories
		# headerRow = "Computer Name, JSS ID"
		# members += [ headerRow ]

		for computer in computers.findall('computer'):
			# compID = computer.find('id').text
			name = computer.find('name').text
			computerInfo = str(name)
			computerInfo = cleanupOutput(computerInfo)
			#print computerInfo.encode('ascii', 'ignore')
			members += [ computerInfo ]

		for g in groups.findall('computer_group'):
			group_name = g.find('name').text
			groupInfo = str(group_name)
			comp_groups += [ groupInfo ]


		print '\nPOLICY SCOPE INFORMATION:'
		print 'Scoped to All Computers: ' + str(allcomputers)
		print '\nCOMPUTER GROUPS IN SCOPE: '
		print '\n'.join (sorted(comp_groups))

		if members:
			print '\nADDITIONAL COMPUTERS IN SCOPE: '
			print '\n'.join (sorted(members))
			print '\nTotal Computers in Scope: ' + str(len(members))

		## Package Configuration Information
		pkgconfig = responseXml.find('package_configuration')
		packages = pkgconfig.find('packages')
		pkgheaderRow = "Package Name"
		pkglist = []

		for pkg in packages.findall('package'):
			pkg_name = pkg.find('name').text
			pkg_action = pkg.find('action').text
			pkgInfo = str(pkg_name) + ', ' + str(pkg_action)
			pkgInfo = cleanupOutput(pkgInfo)
			pkglist += [ pkgInfo ]


		print '\nPACKAGE CONFIGURATION: '
		print '\n'.join (sorted(pkglist))

	else:
		print 'Failed to find policy with ID ' + policyid
