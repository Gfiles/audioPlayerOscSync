from pythonosc import udp_client #uv add python-osc
import subprocess
import json
import os
import sys

def readConfig(settingsFile):
    if os.path.isfile(settingsFile):
        with open(settingsFile) as json_file:
            data = json.load(json_file)
    else:
        data = {
            "oscIPs": ["127.0.0.1", "192.168.132.9"],
            "oscPorts": [8010, 8010],
            "oscAddress" : "/playVideo",
            "audioFile" : "bigBuckFullHD.mp4",
            "videoPlayer" : ["mpv", "--no-video"],
            "loopCommand" : "--loop",
            "repeatOSC" : True
        }
        # Serializing json
        json_object = json.dumps(data, indent=4)
 
        # Writing to config.json
        with open(settingsFile, "w") as outfile:
            outfile.write(json_object)
    return data

def killProcess(processName):
	subprocess.run(["taskkill", "/IM", processName, "/F"])

def installMediaPlayer():
    if videoPlayer[0] == "mpv":
        #install mpv
        print("Installing mpv")
        subprocess.run(["winget", "install", "mpv", "--disable-interactivity", "--nowarn", "--accept-package-agreements", "--accept-source-agreements"])
        print("Installation of MPV complete")
        return True
    else:
        print(f"Video Player is not installed, please install player {audioPlayer}, exiting...")
        return False

# Get the current working
# directory (CWD)

try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
if getattr(sys, 'frozen', False):
    cwd = os.path.dirname(sys.executable)
else:
    cwd = os.path.dirname(this_file)

settingsFile = os.path.join(cwd, "appConfig.json")
config = readConfig(settingsFile)
oscIPs = config["oscIPs"]
oscPorts = config["oscPorts"]
oscAddress = config["oscAddress"]
audioFile = config["audioFile"]
videoPlayer = config["videoPlayer"]
loopCommand = config["loopCommand"]
repeatOSC = config["repeatOSC"]

#print("Current working directory:", cwd)
killProcess('mpv')
running = True
#Teste if mpv Exists
try:
    videoPlaying = subprocess.Popen([videoPlayer[0]], stdout = subprocess.DEVNULL) #do not show output
    videoPlaying.wait()
except FileNotFoundError:
    running = installMediaPlayer()

# Configure OSC Clients
oscClients = list()
for i in range(len(oscIPs)):
	oscClients.append(udp_client.SimpleUDPClient(oscIPs[i], oscPorts[i]))

if os.path.isfile(settingsFile):
    videoPlayer.append(audioFile)
else:
    running = False

while running:
	if repeatOSC:
		#Play Audio
		audioPlayer = subprocess.Popen(videoPlayer)
	else:
		videoPlayer.append(loopCommand)
		subprocess.Popen(videoPlayer)
		running = False
	
    # send OSC Messages to sync video
	for oscClient in oscClients:
		oscClient.send_message(oscAddress, 1)
		print("Message Sent")
	if repeatOSC:
		audioPlayer.wait()
print("Exiting Program")