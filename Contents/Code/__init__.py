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

	oc = ObjectContainer()

	# test
        if Platform.OS in ('MacOSX') and (not IsPrismatikRunning()):
			oc.add(LaunchPrismatikObject())

	else:

		try:
			Profiles       = GetProfiles()
			CurrentProfile = GetCurrentProfile()
			LightpackOn    = IsLightpackOn()
		
			if ( LightpackOn ):
				current_thumb   = R('lightpack.png')
				on_off_title    = 'Turn Lights Off'
				on_off_callback = Callback(LightsOff)
			else:
				current_thumb   = R('lightpack-off.png')
				on_off_title    = 'Turn Lights On'
				on_off_callback = Callback(LightsOn)

			# add item for each profile
			for profileId in Profiles:

				if (profileId == CurrentProfile):
					status = ' (Active)'
				else:
					status = ''
		
				item = PopupDirectoryObject(
					key   = Callback(SetProfile, profileId=profileId),
					title = profileId+status,
					thumb = current_thumb
				)
				oc.add(item)

			# Add item for turning lights on/off
			item = PopupDirectoryObject(
				key   = on_off_callback,
				title = on_off_title,
				thumb = current_thumb
				)

			oc.add(item)

		except:
			# Add popup for no-connection
			item = PopupDirectoryObject(
				key   = Callback(ErrorCallback, error=L('Check_Preferences')),
				title = L('No_Prismatik_connect'),
				thumb = R('error.png')
				)
			oc.add(item)

        	if Platform.OS in ('MacOSX') and IsPrismatikRunning():
			oc.add(QuitPrismatikObject(current_thumb))

	# Add item for setting preferences	
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
       		LightpackDisconnect(lpack)
	except:
		Log("Unable to connect to Prismatik")
		#HTTP.Request('http://localhost:32400/:/plugins/com.plexapp.plugins.prismatik_remote/prefs/set?prismatik_ip=127.0.0.1&prismatik_port=3636', immediate=True)
		return ObjectContainer(header='Error', message=L('No_Prismatik_connect'))

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
# Activates a Prismatik profile and turns on the lights
####################################################################################################
@route(PREFIX + '/select_profile')
def SetProfile(profileId):
	lpack = LightpackConnect()
	lpack.setProfile(profileId)
	lpack.turnOn()
        LightpackDisconnect(lpack)
	oc = ObjectContainer()
	oc.header = NAME
	oc.message = 'Profile "%s" enabled' % profileId
	return oc

####################################################################################################
# Turns on the lights 
####################################################################################################
@route(PREFIX + '/lights_on')
def LightsOn():
	lpack = LightpackConnect()
        lpack.turnOn()
        LightpackDisconnect(lpack)
	oc = ObjectContainer()
	oc.header = NAME
	oc.message = 'Lights turned on'
	return oc
 
####################################################################################################
# Turns off the lights 
####################################################################################################
@route(PREFIX + '/lights_off')
def LightsOff():
	lpack = LightpackConnect()
        lpack.turnOff()
        LightpackDisconnect(lpack)
	oc = ObjectContainer()
	oc.header = NAME
	oc.message = 'Lights turned off'
	return oc


####################################################################################################
# Returns a list of profiles defined in Prismatik 
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
        lpack = lightpack.lightpack(remote_ip,int(remote_port),[1,2,3,4,5,6,7,8,9,10], " ")
	out=lpack.connect()

	if ( out == -1 ):
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
#  Show error message 
####################################################################################################
@route(PREFIX + '/error')
def ErrorCallback(error):
	return ObjectContainer(header='Error', message=error)
	
####################################################################################################
# Check if Prismatik application is running 
####################################################################################################
def IsPrismatikRunning():
	applescript = """tell application "System Events" to count (every process whose name is "Prismatik")"""
	return execAppleScript(applescript) == "1"
	
####################################################################################################
# Returns object to Quit the Prismatik app
####################################################################################################
def QuitPrismatikObject(thumb):
	return PopupDirectoryObject(
		key   = Callback(QuitPrismatikCallback),
		title = 'Quit Prismatik',
		thumb = thumb,
	)

####################################################################################################
# Executes Applescript to Quit the Prismatik app
####################################################################################################
def QuitPrismatikCallback():
	applescript = """tell application "Prismatik" to quit"""
	execAppleScript(applescript)
	oc = ObjectContainer()
	oc.header = NAME
	oc.message = 'Prismatik has exited'
	return oc
	
####################################################################################################
# Returns object to Launch the Prismatik app
####################################################################################################
def LaunchPrismatikObject():
	return PopupDirectoryObject(
		key   = Callback(LaunchPrismatikCallback),
		title = 'Launch Prismatik',
		thumb = R('lightpack-off.png'),
	)

####################################################################################################
# Executes Applescript to Launch the Prismatik app
####################################################################################################
def LaunchPrismatikCallback():
	applescript = """tell application "Prismatik" to run"""
	execAppleScript(applescript)
	oc = ObjectContainer()
	oc.header = NAME
	oc.message = 'Prismatik has started'
	return oc

####################################################################################################
# Executes an AppleScript
####################################################################################################
def execAppleScript(*applescripts):	
	cmd = 'osascript'
	for applescript in applescripts:
		cmd += " -e '" +  applescript + "'"
	return execShellCommand(cmd)
	
####################################################################################################
# Executes shell command
####################################################################################################
def execShellCommand(cmd):
	f = os.popen(cmd)
	output = f.readlines()
	if len(output) > 0:
		result = output[0].replace('\n', '')
		return result
	return ''

