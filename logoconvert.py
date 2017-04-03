import math
import sys
import time
import random

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
import pickle

img = Image.open(sys.argv[1])


def find_palette(point):
	rgb_code_dictionary = {
		(255, 255, 255): 0,
		(228, 228, 228): 1,
		(136, 136, 136): 2,
		(34, 34, 34): 3,
		(255, 167, 209): 4,
		(229, 0, 0): 5,
		(229, 149, 0): 6,
		(160, 106, 66): 7,
		(229, 217, 0): 8,
		(148, 224, 68): 9,
		(2, 190, 1): 10,
		(0, 211, 211): 11,
		(0, 131, 199): 12,
		(0, 0, 234): 13,
		(207, 110, 228): 14,
		(130, 0, 128): 15
	}

	def distance(c1, c2):
		(r1, g1, b1) = c1
		(r2, g2, b2) = c2
		return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

	colors = list(rgb_code_dictionary.keys())
	closest_colors = sorted(colors, key=lambda color: distance(color, point))
	closest_color = closest_colors[0]
	code = rgb_code_dictionary[closest_color]
	return code



width = 37
height = 14

total = width * height

imggrid = []

for y in range(height ):
	imgrow = []
	for x in range(width ):
		print(x,y)
		pixel = img.getpixel((x,y))

		if pixel[3] > 0:
			pal = find_palette((pixel[0], pixel[1], pixel[2]))
			imgrow.append(pal)
		else:
			imgrow.append(-1)
	imggrid.append(imgrow)


print imggrid
pickle.dump(imggrid,open("sbulogo.pickle","wb"))
