import os, inspect

scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
scriptName = os.path.basename(__file__)
newpath = os.path.split(scriptPath)
scriptLocation = newpath[0] + '/' + 'CasperAPI_CLI.py'
basePath = newpath[0]

def getJSS_API_URL():
	#scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	#print("Script Path: {}".format(basePath))
	jss_api_url_Location = basePath + '/.jssURL'
	#print("jss api url location: {}".format(jss_api_url_Location))

	if os.path.isfile(jss_api_url_Location):

		with open (jss_api_url_Location) as jssURLfile:
			jssURL = jssURLfile.read().replace('\n','')
			jss_api_url = jssURL + '/JSSResource'
			return jss_api_url
