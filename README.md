# Casper API CLI

What is it?
-----------

This is a command line tool for interacting with the JSS via the command line.

### Dependencies

The Casper API CLI has been tested on Python 2.7.10 and Mac OS X El Capitan, and requires specific Python libraries.

- urllib2
- base64
- xml.etree
- xml.dom

Your Mac should probably have these Python libraries already. However, upon running it the first time, you may be prompted to install some of these libraries. You can typically install them using `pip install LIBRARYNAME` or `easy-install LIBRARYNAME`.

### Setup

1. Download the `[CasperAPI_CLI.py](https://github.com/eventbrite/Casper-API-CLI/blob/master/CasperAPI_CLI.py)` and `[SetupCasperAPI.py](https://github.com/eventbrite/Casper-API-CLI/blob/master/SetupCasperAPI.py)` scripts from this repository.
2. Place that folder inside an encrypted disk image for security purposes. 

  To create an encrypted disk image, you can use the following command to create a 10MB encrypted container named casperapi.dmg that is mounted as a volume called "CasperAPI" and then create a second 10MB encrypted container named keys.dmg that is mounted as a volume called "Keys". The setup script will store the encryption keys to decrypt your JSS password in this container.

  ```
  hdiutil create casperapi.dmg -encryption -size 10MB -volname "CasperAPI" -fs JHFS+
  ```

  You will then be prompted to enter a password for your encrypted container:


  ```Enter a new password to secure "casperapi.dmg":
  Re-enter new password:
  ........................................................................................................................................................................................................................................................................................
  created: /Users/casper/Documents/casperapi.dmg
  ```

  Next create the Keys encrypted container:

  ```
  hdiutil create keys.dmg -encryption -size 10MB -volname "Keys" -fs JHFS+
  ```

  Mount the newly created casper api disk image:

  ```hdiutil attach casperapi.dmg```

  You will be prompted for the password to mount the volume.

  Mount the newly created keys disk image:

  ```hdiutil attach keys.dmg```

  Navigate to the CasperAPI mounted volume:

  ```cd /Volumes/CasperAPI/```

  Then create a folder to copy the Casper API scripts and navigate to that folder:

  ```
  mkdir CasperAPI_CLI
  cd CasperAPI_CLI
  ```

  Download the latest release via curl or via the web:

  ```curl -L https://github.com/eventbrite/Casper-API-CLI/archive/v0.1.0.zip -o casperapi.zip``` 

  Place the scripts `CasperAPI_CLI.py` and `SetupCasperAPI.py` in this container. To unzip it via command line:

  ```unzip casperapi.zip``` 

3. Generate an encrypted string for your JSS password using `SetupCasperAPI.py`. To get started, navigate to your encrypted container in Terminal and enter the following command:

  ```
  python SetupCasperAPI.py
  ```

  You will then be prompted to enter information to connect to the JSS.

  - The JSS URL, without https://, e.g. `yourjss.jamfcloud.com`
  - Your JSS username
  - Your JSS password
  - The path to a location different than the location where you've set up the CasperAPI_CLI script to store your encryption keys. We set this up above as `/Volumes/Keys`


  ```
  hostname:CasperAPI_CLI host$ python SetupCasperAPI.py
  Welcome to the Casper CLI setup. Please note that this will overwrite any configuration files you have previously configured.

  Enter JSS URL in the form yourjss.jamfcloud.com: yourjss.jamfcloud.com
  Username: your-jss-username
  Password:
  Enter full path to the location to store encryption keys, in the form /Path/To/Folder : /Volumes/Keys

  Setup is complete, run python CasperAPI_CLI.py -h to get started, or set up your bash profile (step 5 below) to create an alias.
  ```

4. To make it easier to call the Casper API CLI, set an alias in your bash profile. Open the file ~/.bash_profile in a text editor, and add the line:

  ```
  alias casper="python /Volumes/CasperAPI/CasperAPI_CLI/CasperAPI_CLI.py"
  ```

  where you enter the full path to the downloaded `CasperAPI_CLI.py` script.

  Reload your bash profile:

  ```
  source ~/.bash_profile
  ```

5. You're ready to go. Try a simple command like:

  ```
  casper getcomputer YOURUSERNAME
  ```

## Usage

### Commands

#### Delete a Computer by JSS ID

This deletes a computer record from the JSS using the JSS computer ID. 

##### Syntax

```
casper deletecomputerbyid JSSID
```

##### Example

```
casper deletecomputerbyid 123
```

The Casper CLI will then provide you the detailed information for the computer and prompt to make sure you really want to delete the computer from the JSS.

```
Are you sure you want to delete the computer above from the JSS? (y/n): n
Aborting request to delete computer 123
```

#### Delete Computers by JSS ID using a CSV File

This deletes computer records specified in a CSV file, using JSS IDs. The CSV file should be formatted with one header row, followed by as many JSS IDs of computers you wish to delete. 

CSV File Example:

| JSS IDs |
| ------- |
| 135     |
| 467     |
| 1032    |

##### Syntax

```
casper deletecomputeridsfromcsv /Full/Path/To/csvfile.csv
```

#### Get a Computer

This returns all computers in the JSS that match the given search string. Optionally, you can specify using `-d yes` or `--detail yes` to output more detailed information for all matches. By default --detail is set to "no"

##### Syntax

```
casper getcomputer SEARCHSTRING -d [yes|no]
```

##### Example

```
casper getcomputer jason -d yes
```

Returns all computers matching the string `jason` with full detail.

#### Unmanage a Computer by JSS ID

This sets a computer to unmanaged in the JSS using the JSS computer ID.

##### Syntax

```
casper unmanagecomputer JSSID
```

##### Example

```
casper unmanagecomputer 123
```

Output

```
Unmanaging computer 123...
Successfully unmanaged computer ID 123...
```

#### Unmanage Computers by JSS ID using a CSV File

This unmanages computer records specified in a CSV file, using JSS IDs. The CSV file should be formatted with one header row, followed by as many JSS IDs of computers you wish to set as unmanaged.

CSV File Example:

| JSS IDs |
| ------- |
| 135     |
| 467     |
| 1032    |

##### Syntax

```
casper unmanagecomputeridsfromcsv /Full/Path/To/csvfile.csv
```

#### Update Asset Tag of a Computer using JSS ID

This updates the asset tag of a computer using the JSS computer ID.

##### Syntax

```
casper updateassettag JSSID ASSETTAG
```

##### Example

```
casper updateassettag 123 50505
```

Updates the asset tag of JSS computer ID 123 to the number 50505.



## Credits

Functions `decryptString` and `GenerateEncryptedString` derived from https://github.com/jamfit/Encrypted-Script-Parameters, 
Copyright (c) 2015, JAMF Software, LLC. All rights reserved.

## License

Copyright (c) 2016, Eventbrite.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.




