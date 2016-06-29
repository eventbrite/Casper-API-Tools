#!/usr/bin/python

# GenerateEncryptedString method derived from https://github.com/jamfit/Encrypted-Script-Parameters

# Python wrapper for 'openssl' to create an encrypted Base64 string for script parameters
# Additional layer of security when passing account credentials from the JSS to a client
import subprocess
import sys
import getpass
import ConfigParser
import os, inspect

# Use GenerateEncryptedString() locally - DO NOT include in the script!
# The 'Encrypted String' will become a parameter for the script in the JSS
# The unique 'Salt' and 'Passphrase' values will be present in your script
def GenerateEncryptedString(inputString, scriptLoc, keysLoc):
    '''Usage >>> GenerateEncryptedString("String")'''
    salt = subprocess.check_output(['/usr/bin/openssl', 'rand', '-hex', '8']).rstrip()
    passphrase = subprocess.check_output(['/usr/bin/openssl', 'rand', '-hex', '12']).rstrip()
    p = subprocess.Popen(['/usr/bin/openssl', 'enc', '-aes256', '-a', '-A', '-S', salt, '-k', passphrase], stdin = subprocess.PIPE, stdout = subprocess.PIPE)
    encrypted = p.communicate(inputString)[0]

    jsspwLoc = scriptLoc + '/.jsspwencrypted'
    jsspwFile = open(jsspwLoc, 'w+')
    jsspwFile.write(encrypted)

    saltLoc = keysLoc + '/.jsssalt'
    saltFile = open(saltLoc, 'w+')
    saltFile.write(salt)

    passphraseLoc = keysLoc + '/.jsspassphrase'
    passphraseFile = open (passphraseLoc, 'w+')
    passphraseFile.write(passphrase)

    print '\nSetup is complete, run python CasperAPI_CLI.py -h to get started, or set up your bash profile to create an alias.\n'

    #print("Encrypted String: %s" % encrypted)
    #print("Salt: %s | Passphrase: %s" % (salt, passphrase))

def main():
	scriptLoc = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

	print 'Welcome to the Casper CLI setup. Please note that this will overwrite any configuration files you have previously configured.\n'

	# Get JSS URL
	try:
		jssURL = raw_input('Enter JSS URL in the form yourjss.jamfcloud.com: ')
		jssURL = 'https://' + jssURL
		jssURLLoc = scriptLoc + '/.jssURL'
		jssURLFile = open(jssURLLoc, 'w+')
		jssURLFile.write(jssURL)
	except:
		print '\nCtrl-C detected, exiting...'
		raise SystemExit


	# Get JSS username
	try:
		username = raw_input('Username: ')
		usernameLoc = scriptLoc + '/.jssusername'
		usernameFile = open(usernameLoc, 'w+')
		usernameFile.write(username)
	except:
		print '\nCtrl-C detected, exiting...'
		raise SystemExit


	# Get user password
	try:
		userPW = getpass.getpass('Password: ')
	except:
		print '\nCtrl-C detected, exiting...'
		raise SystemExit

	
	# Set Keys location file
	try:
		keysLoc = raw_input('Enter full path to the location to store encryption keys, in the form /Path/To/Folder : ')
		keysLocFullPath = scriptLoc + '/.keysfile'
		keysFile = open(keysLocFullPath, 'w+')
		keysFile.write(keysLoc)
	except:
		print '\nCtrl-C detected, exiting...'
		raise SystemExit

	GenerateEncryptedString(userPW, scriptLoc, keysLoc)

if __name__ == '__main__':
    main()