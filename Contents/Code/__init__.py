import os
import time
import lightpack

	
####################################################################################################

PREFIX = "/music/Prismatik_Remote"
NAME   = 'Prismatik Remote'
ART    = 'Airfoil.png'
THUMB  = 'Airfoil.png'


####################################################################################################
def Start():
	Log("Starting Prismatik Remote")
	#Plugin.AddPrefixHandler(APPLICATIONS_PREFIX, MainMenu, 'Airfoil', ICON, ART)
        Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
        Plugin.AddViewGroup('Details', viewMode='InfoList', mediaType='items')

	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	ObjectContainer.view_group = 'List'

def ValidatePrefs():
	remote_ip = Prefs['prismatic_ip']
	remote_port = Prefs['prismatic_port']
	lpack = lightpack.lightpack(remote_ip,int(remote_port),[1,2,3,4,5,6,7,8,9,10])
	try:
		lpack.connect()
		lpack.disconnect()
		return MessageContainer(
			"Successfuly Connected to Prismatik",
			"Ok"
		)
	except:
		return MessageContainer(
			"Error: Cannot connect to Prismatik",
			"Please check settings"
		)

####################################################################################################
@handler(PREFIX, NAME, art=R(ART), thumb=R(THUMB))
def MainMenu():
	Log("Prismatik Remote MainMenu")
	oc = ObjectContainer()
	remote_ip = Prefs['prismatic_ip']
	remote_port = Prefs['prismatic_port']
	lpack = lightpack.lightpack(remote_ip,int(remote_port),[1,2,3,4,5,6,7,8,9,10])

	lpack.connect()
	Profiles = GetProfiles(lpack)
	CurrentProfile = GetCurrentProfile(lpack)
	lpack.disconnect()
	for profileId in Profiles:

		if (profileId == CurrentProfile):
			status = " ("+L("Active") + ")"
		else:
			status = ""
		
		item = PopupDirectoryObject(
			key = Callback(SetProfile, profileId=profileId),
			title = profileId+status,
			summary=status,
			art=R(ART)
		)
		oc.add(item)

	item = PopupDirectoryObject(
		key = Callback(LightsOff),
		title = 'Turn Lights Off',
		summary='Summary',
		art=R(ART)
		)

	oc.add(item)

	
	#except:
		#AddErrorObject(oc, L("No_Prismatik_found"), L("Install_Prismatik_Error"), R("Airfoil-error.png"))
	oc.add(PrefsObject(title = L('Preferences'), thumb = R('icond-prefs.png')))

	return oc



def toArray(arrayStr):
	return arrayStr.split(", ")	
	
def GetProfiles(lpack):
	lpack.lock()
	profiles = lpack.getProfiles()
	lpack.unlock()
	return profiles[:(len(profiles)-1)]

def GetCurrentProfile(lpack):
	lpack.lock()
	profile = lpack.getProfile()
	lpack.unlock()
	return profile.strip()

def execShellCommand(cmd):
	f = os.popen(cmd)
	output = f.readlines()
	if len(output) > 0:
		result = output[0].replace("\n", "")
		return result
	return ""

def execAppleScript(*applescripts):	
	cmd = "osascript"
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

def AddErrorObject(oc, title, error, image):
	item = DirectoryObject(
		key=Callback(ErrorCallback, error=error),
		title=title,
		summary=error,
		thumb=image,
		art=R(ART)
	)
	oc.add(item)

@route(PREFIX+'/set_profile')
def SetProfile(profileId):
        remote_ip = Prefs['prismatic_ip']
        remote_port = Prefs['prismatic_port']
        lpack = lightpack.lightpack(remote_ip,int(remote_port),[1,2,3,4,5,6,7,8,9,10])
        lpack.connect()
	lpack.lock()
	lpack.turnOn()
	lpack.setProfile(profileId)
	lpack.unlock()	
	lpack.disconnect()
	return MainMenu()
  
@route(PREFIX+'/lights_off')
def LightsOff():
        remote_ip = Prefs['prismatic_ip']
        remote_port = Prefs['prismatic_port']
        lpack = lightpack.lightpack(remote_ip,int(remote_port),[1,2,3,4,5,6,7,8,9,10])
        lpack.connect()
        lpack.lock()
        lpack.turnOff()
        lpack.unlock()  
        lpack.disconnect()
	return MainMenu()

def QuitPrismatikCallback():
	QuitPrismatik()
	return MainMenu()
	
def LaunchPrismatikCallback():
	LaunchPrismatik()
	return MainMenu()

def ErrorCallback(error):
	return ObjectContainer(title=error)

	
