import os
import time
import lightpack

	
####################################################################################################

PREFIX       = "/video/Prismatik_Remote"
NAME         = 'Prismatik Remote'
ART          = 'prismatik.png'
ICON         = 'prismatik.png'
PREFS_ICON   = 'settings.png'
PROFILE_ICON = 'lightpack.png'

####################################################################################################

####################################################################################################
# Start function
####################################################################################################
def Start():

	Log('Starting Prismatik Remote')

	HTTP.CacheTime = 0
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	#ObjectContainer.replace_parent = True
	ValidatePrefs()


####################################################################################################
# Main menu
####################################################################################################
@handler(PREFIX, NAME, art=R(ART), thumb=R(ICON))
def MainMenu():

	Log('Prismatik Remote MainMenu')
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
	Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')

	oc = ObjectContainer(view_group='List')

	try:
		Profiles = GetProfiles()
		CurrentProfile = GetCurrentProfile()

		oc.add(PopupDirectoryObject( key=Callback(ListProfiles),
					     title='Set Profile ('+CurrentProfile+')',
					     summary=CurrentProfile,
                                             thumb=R('lightpack.png')))

	#	for profileId in Profiles:

	#		if (profileId == CurrentProfile):
	#			status = ' ('+L('Active') + ')'
	#		else:
	#			status = ''
	#	
	#		item = PopupDirectoryObject(
	#			key = Callback(SetProfile, profileId=profileId),
	#			title = profileId+status,
	#			summary=status,
	#			thumb=R('lightpack.png'),
	#			#replace_parent=True,
	#			#no_cache=True
	#		)
	#		oc.add(item)

		# Add item for turning lights off
		if ( IsLightpackOn() ):
			item = PopupDirectoryObject(
				key = Callback(LightsOff),
				title = 'Turn Lights Off',
				summary='Turn Lights Off',
				thumb=R('lightpack.png')
				)
		else:
			item = PopupDirectoryObject(
				key = Callback(LightsOn),
				title = 'Turn Lights On',
				summary='Turn Lights On',
				thumb=R('lightpack.png')
				)

		oc.add(item)

	except:
		AddErrorObject(oc, L('No_Prismatik_connect'), L('Check_Preferences'), R('error.png'))

	
	oc.add(PrefsObject(title = L('Preferences'), thumb = R(PREFS_ICON)))

	return oc


####################################################################################################
# Called by the framework every time a user changes the prefs
####################################################################################################
@route(PREFIX + '/ValidatePrefs')
def ValidatePrefs():

	Log('Validating Prefs')
	if Prefs['RESET']:
		ResetPrefs()

	try:
        	lpack = LightpackConnect()
	except:
		Log("Unable to connect to Prismatik")
		HTTP.Request('http://localhost:32400/:/plugins/com.plexapp.plugins.prismatik_remote/prefs/set?prismatik_ip=127.0.0.1&prismatik_port=3636', immediate=True)
		return ObjectContainer(header='Error', message=L('No_Prismatik_connect'))

       	LightpackDisconnect(lpack)
	return 

####################################################################################################
# Reset the Preferences to the defaults
####################################################################################################
@route(PREFIX + '/ResetPrefs')
def ResetPrefs():
	myHTTPPrefix = 'http://localhost:32400/:/plugins/com.plexapp.plugins.prismatik_remote/prefs/'
	myURL = myHTTPPrefix + 'set?RESET=False&prismatik_ip="127.0.0.1"&prismatik_port="3636"'
	HTTP.Request(myURL, immediate=True)


####################################################################################################
# Popup for user to select profile
####################################################################################################
@route(PREFIX + '/list_profiles')
def ListProfiles():

	oc = ObjectContainer(title2='Select a Profile', replace_parent=True,view_group='List')

	Profiles = GetProfiles()
	CurrentProfile = GetCurrentProfile()

	for profileId in Profiles:

		if (profileId == CurrentProfile):
			status = ' ('+L('Active') + ')'
		else:
			status = ''
	
		item = PopupDirectoryObject(
			key = Callback(SetProfile, profileId=profileId),
			title = profileId+status,
			summary=profileId+status,
			thumb=R('lightpack.png'),
		)
		oc.add(item)

	return oc

####################################################################################################
# Activates a Prismatik profile and turns on the lights
####################################################################################################
@route(PREFIX + '/list_profiles/select_profile')
def SetProfile(profileId):
	lpack = LightpackConnect()
	lpack.setProfile(profileId)
	lpack.turnOn()
        LightpackDisconnect(lpack)
	return MainMenu()

####################################################################################################
# Turns on the lights 
####################################################################################################
def LightsOn():
	lpack = LightpackConnect()
        lpack.turnOn()
        LightpackDisconnect(lpack)
	return MainMenu()
 
####################################################################################################
# Turns off the lights 
####################################################################################################
def LightsOff():
	lpack = LightpackConnect()
        lpack.turnOff()
        LightpackDisconnect(lpack)
	return MainMenu()

####################################################################################################
# Returns a list of prifiles defined in Prismatik 
####################################################################################################
def GetProfiles():
	lpack = LightpackConnect()
	profiles = lpack.getProfiles()
        LightpackDisconnect(lpack)
	return profiles[:(len(profiles)-1)]

####################################################################################################
# Returns the name of the currently active profile 
####################################################################################################
def GetCurrentProfile():
	lpack = LightpackConnect()
	profile = lpack.getProfile().strip()
        LightpackDisconnect(lpack)
	return profile

####################################################################################################
# Returns True if lights are on 
####################################################################################################
def IsLightpackOn():
	lpack = LightpackConnect()
	status = lpack.getStatus().strip()
        LightpackDisconnect(lpack)
	if status == 'on':
		return True
	else:
		return False

####################################################################################################
# Connects to Prismatik server and returns a 'lightpack' handle 
####################################################################################################
def LightpackConnect():
	remote_ip = Prefs['prismatik_ip']
        remote_port = Prefs['prismatik_port']
        lpack = lightpack.lightpack(remote_ip,int(remote_port),[1,2,3,4,5,6,7,8,9,10])
	out=lpack.connect()
	if ( out == -1 ):
		Log(out)
		raise Exception('Connection Error') 
	else:
        	lpack.lock()
		return lpack

####################################################################################################
# Disconnects from Prismatik 
####################################################################################################
def LightpackDisconnect(lpack):
	lpack.unlock()
	lpack.disconnect()

####################################################################################################
# Creates error entry if cannot connect to Prismatik 
####################################################################################################
def AddErrorObject(oc, title, error, image):
	item = DirectoryObject(
		key=Callback(ErrorCallback, error=error),
		title=title,
		summary=error,
		thumb=R(ICON),
		art=R(ART)
	)
	oc.add(item)


def QuitPrismatikCallback():
	QuitPrismatik()
	return MainMenu()
	
def LaunchPrismatikCallback():
	LaunchPrismatik()
	return MainMenu()

def ErrorCallback(error):
	return ObjectContainer(title=error)

	
def execShellCommand(cmd):
	f = os.popen(cmd)
	output = f.readlines()
	if len(output) > 0:
		result = output[0].replace('\n', '')
		return result
	return ''

def execAppleScript(*applescripts):	
	cmd = 'osascript'
	for applescript in applescripts:
		cmd += " -e '" +  applescript + "'"
	return execShellCommand(cmd)
	
def IsApplicationExists(applicationID):
	#return execAppleScript("""tell application "Finder\"""", "try", """exists application file id \"""" + applicationID + """\"""", "true", "on error", "false", "end try", "end tell") == "true"
	return 1

def IsPrismatikRunning():
	applescript = """tell application "System Events" to count (every process whose name is "Prismatik")"""
	return execAppleScript(applescript) == "1"
	
def QuitPrismatik():
	applescript = """tell application "Prismatik" to quit"""
	execAppleScript(applescript)

def LaunchPrismatik():
	applescript = """tell application "Prismatik" to run"""
	execAppleScript(applescript)


