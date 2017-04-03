import urllib.request
import random
import pickle
import requests
from requests.adapters import HTTPAdapter
import sys
import time

version = 3
verbose = False
logodata = None

def version_check():
	latest_ver = "https://pastebin.com/raw/J8kMBwRW"
	latest_ver = urllib.request.urlopen(latest_ver)
	latest_ver = int(str(latest_ver.read())[2:-1])

	if (latest_ver != version):
		print("You are running an outdated version of this script! Get the latest one from . See the post on the SBCS fb for updates.")
		quit()
	else:
		print("version check: you are running the latest version")

def place_pixel(ax, ay, new_color):
	message = "Probing absolute pixel {},{}".format(ax, ay)

	result = False

	while True:
		r = s.get("http://reddit.com/api/place/pixel.json?x={}&y={}".format(ax, ay), timeout=5)
		if r.status_code == 200:
			data = r.json()
			break
		else:
			print("ERROR: ",r,r.text)
		time.sleep(5)

	old_color = data["color"] if "color" in data else -1
	if old_color == new_color:
		if verbose:
			print("{}: skipping, color #{} set by {}".format(message, new_color, data[
				"user_name"] if "user_name" in data else "<nobody>"))
		time.sleep(.25)
	else:
		colorstring = ["white","black","red"]
		print("{}: Placing color {}".format(message, colorstring[int(new_color/2)], ax, ay))
		r = s.post("https://www.reddit.com/api/place/draw.json",
				   data={"x": str(ax), "y": str(ay), "color": str(new_color)})
		secs = float(r.json()["wait_seconds"])
		if "error" not in r.json():
			message = "Placed color, waiting {} seconds."
			result = True
		else:
			message = "Cooldown already active - waiting {} seconds."
		waitTime = int(secs) + 2
		while(waitTime > 0):
			m = message.format(waitTime)
			time.sleep(1)
			waitTime -= 1
			if waitTime > 0:
				print(m, end="              \r")
			else:
				print(m)

		if "error" in r.json():
			place_pixel(ax, ay, new_color)
	return result

def download_img_data():
	#download the image file
	logofileurl = "http://www.shaansweb.com/sbulogo.pickle"
	logofile = urllib.request.urlopen(logofileurl)
	data = logofile.read()
	logofile.close()
	with open("sbulogo.pickle", "wb") as f :
		f.write(data)

	#open the image file
	global logodata	
	logodata = pickle.load(open("sbulogo.pickle","rb"))

def main():

	download_img_data()

	#get the coordinates where we'll draw
	coordinateurl = "https://pastebin.com/raw/wtH4uGet"
	origin_coordinates = urllib.request.urlopen(coordinateurl)
	origin_coordinates = [int(x) for x in str(origin_coordinates.read())[2:-1].split(" ")]
	
	print("Successfully authenticated " + username + "\nDrawing SBU logo at " + str(origin_coordinates) + "\n")
	width = len(logodata[0])
	height = len(logodata)
	print(height)

	while True:

		placedtile = False

		
		for x in range(width):
			#refresh origin coordinates
			origin_coordinates_refresh = urllib.request.urlopen(coordinateurl)
			origin_coordinates_refresh = [int(x) for x in str(origin_coordinates_refresh.read())[2:-1].split(" ")]

			if (origin_coordinates_refresh != origin_coordinates):
				origin_coordinates = origin_coordinates_refresh
				download_img_data()

			for y in range(height):

				#get random coordinates in the pic
				####local_coordinates = locationsArray[y][x]
				local_coordinates = [x,y]
				pixel  = logodata[local_coordinates[1]][local_coordinates[0]]

				if pixel > -1:
					#convert to global coordinates
					x_coor = origin_coordinates[0] + local_coordinates[0]
					y_coor = origin_coordinates[1] + local_coordinates[1]
					#get the color
					#draw it
					placedtile = place_pixel(x_coor,y_coor,pixel)

				if placedtile:
					break
			if placedtile:
				break

		if (not placedtile):
			message = "All pixels placed, sleeping {}s..."
			waitTime = 10
			while(waitTime > 0):
				m = message.format(waitTime)
				time.sleep(1)
				waitTime -= 1
				if waitTime > 0:
					print(m, end="              \r")
				else:
					print(m)

if len(sys.argv) < 3:
	print("usage: python3 redditPlaceSBU.py <username> <pass>")
	quit()


version_check()
#get user and pass from command
username = sys.argv[1]
password = sys.argv[2]

if len(sys.argv) >= 4:
	verbose = True

#log into reddit
s = requests.Session()
s.mount('https://www.reddit.com', HTTPAdapter(max_retries=5))
s.headers["User-Agent"] = "PlacePlacer"
r = s.post("https://www.reddit.com/api/login/{}".format(username),
		   data={"user": username, "passwd": password, "api_type": "json"})
try:
	s.headers['x-modhash'] = r.json()["json"]["data"]["modhash"]
except Exception as e:
	print("invalid credentials")
	quit()
main()
