import os, inspect

def getJSS_API_URL():
	scriptPath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	print scriptPath
	jss_api_url_Location = scriptPath + '/.jssURL'

	if os.path.isfile(jss_api_url_Location):

		with open (jss_api_url_Location) as jssURLfile:
			jssURL = jssURLfile.read().replace('\n','')
			jss_api_url = jssURL + '/JSSResource'
			return jss_api_url
