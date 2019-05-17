import sys
sys.path.append('..')
from utilities import jamfconfig
from utilities import apirequests
import xml.etree.ElementTree as etree

jss_api_base_url = jamfconfig.getJSS_API_URL()