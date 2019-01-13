from PIL import Image
import numpy as np
import os, sys
import glob
from random import shuffle
import random
from tqdm import tqdm
from math import *
from PIL import ImageDraw


def progress_bar(iteration, total, barLength=50):
    percent = int(round((iteration / total) * 100))
    nb_bar_fill = int(round((barLength * percent) / 100))
    bar_fill = '#' * nb_bar_fill
    bar_empty = ' ' * (barLength - nb_bar_fill)
    sys.stdout.write("\r  [{0}] {1}%".format(str(bar_fill + bar_empty), percent))
    sys.stdout.flush()

def Pass(IN1, IN2, OUT, N):

	im = Image.open(IN1)
	width, height = im.size

	im2 = Image.open(IN2)
	width2, height2 = im2.size

	X = np.random.randint(min(width2, width), size=N)
	Y = np.random.randint(min(height2,height), size=N)


	for i in range(N):
		im.putpixel((X[i],Y[i]), im2.getpixel((int(X[i]),int(Y[i]))))
	im.save(OUT)

def Mainou(IN1, IN2, OUT, N, EPOCHS):

	os.system("rm -f OUT/*")
	Pass("IN/"+IN1, "IN/"+IN2, "OUT/0.png", N)
	for i in range(1, EPOCHS):
		progress_bar(i, EPOCHS, 60)
		Pass("OUT/"+str(i-1)+".png", "IN/"+ IN2, "OUT/"+str(i)+".png", N)

	os.system("ffmpeg -framerate 30 -i OUT/%d.png -codec copy "+ OUT)

def step(liste, IN1, IN2, OUT):

	im = Image.open(IN1)

	im2 = Image.open(IN2)

	for elem in liste:
		im.putpixel(elem, im2.getpixel(elem))
	im.save(OUT)

def getAllPixels(pix):


	im = Image.open(pix)
	width, height = im.size

	L = []
	for x in range(width):
		L.append([])
		for y in range(height):
			L[x].append((x,y))
	return L

def generatePixel(mu, sigma, L, LEFT = False):

	Continue = True

	if LEFT == True:
		for i in range(mu):
			if len(L[i]) > 0 and mu - i > 40:
				if np.random.choice([0,1], p = [0.95, 0.05]) == 1:
					x = i
					Continue = False
				break
	else :
		for i in range(len(L) - mu):
			if len(L[len(L)-i-1]) > 0 and mu - i > 40:
				if np.random.choice([0,1], p = [0.95, 0.05]) == 1:
					x = len(L)-i-1
					Continue = False
				break		

	if Continue :
		x = int(random.gauss(mu, sigma))
		k = 0
		while x < 0 or x >= len(L) or len(L[x]) == 0 or (LEFT and x > mu and x - mu > 80) or (LEFT == False and x < mu and mu - x > 80):
			x = int(random.gauss(mu, sigma))
			k+= 1
			if k > 10:
				for i in range(len(L)):
					if LEFT and L[i] != []:
						x = i
						break
					elif not LEFT and L[len(L) - i -1] != []:
						x = len(L) - i -1
						break
				break

	if not LEFT and mu in [len(L) - 1] and x < 50:
		print(x)

	i = np.random.randint(len(L[x]))

	x,y = L[x][i]

	del L[x][i]

	return ((x,y), L)

def getPolygon(A_angle, C_angle, size):

	C_angle = 3*np.pi/5 - 0.039751849258575
	l = size/(1-cos(A_angle))
	xa = -l*cos(A_angle)
	ya = 0
	A = (xa, ya)
	B = (xa + l*cos(A_angle), ya + l*sin(A_angle))
	C = (xa, ya + 2*l*sin(A_angle))
	D = (xa + l*cos(C_angle-A_angle), ya + 2*l*sin(A_angle) + l*sin(C_angle-A_angle))
	E = (xa + l, ya)

	poly = [A, B, C, D, E]

	for i in range(len(poly)):
		(t, t2) = poly[i]
		poly[i] = (t, abs(t2 - size))

	return poly


def saveAsPolygon(image, name, length):

	# read image as RGB and add alpha (transparency)
	im = image.convert("RGBA")

	# convert to numpy (for convenience)
	imArray = np.asarray(im)

	# create mask
	poly = getPolygon(3*np.pi/4, 3*np.pi/5, length)
	maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
	ImageDraw.Draw(maskIm).polygon(poly, outline=1, fill=1)
	mask = np.array(maskIm)

	# assemble new image (uint8: 0-255)
	newImArray = np.empty(imArray.shape,dtype='uint8')

	# colors (three first columns, RGB)
	newImArray[:,:,:3] = imArray[:,:,:3]

	# transparency (4th column)
	newImArray[:,:,3] = mask*255

	# we compute symetry in order to don't have to flip them after
	if (int(name[name.rfind('/')+1:]) % 24) % 2 == 0:
		newImArray = np.fliplr(newImArray)

	# back to Image from numpy
	newIm = Image.fromarray(newImArray, "RGBA")
	newIm.save(name + ".png")


def fromFolder(FOLDER, TEMP, N = 1000, EPOCHS = 50, transitionWidth = 100, name="test", wayAndReturn = True, length=300):

	sigma = 50

	files = []
	for file in glob.glob(FOLDER+"/*") :
		files.append(file)
	print(files)

	n = 0
	if not os.path.exists(TEMP):
		os.makedirs(TEMP)
	else:
		os.system("rm -rf "+TEMP)
		os.makedirs(TEMP)

	LEFT = False

	for i in tqdm(range(len(files)-1)):

		im1 = Image.open(files[i])
		im2 = Image.open(files[i+1])

		L = getAllPixels(files[i])

		s = (len(L)*len(L[0])//EPOCHS)
		
		im1.save(TEMP + '/' +str(n) + ".png")
		#saveAsPolygon(im1, TEMP + '/' +str(n), length)

		for k in range(0, EPOCHS):
			for p in range(s*k, s*(k+1)):
				if LEFT :
					(elem, L) = generatePixel((k*len(L))//(EPOCHS), sigma, L, LEFT = True)
				else:
					(elem, L) = generatePixel(((len(L)*EPOCHS - k*len(L)))//(EPOCHS), sigma, L)
				im1.putpixel(elem, im2.getpixel(elem))

			im1.save(TEMP + '/' +str(n+1) + ".png")
			#saveAsPolygon(im1, TEMP + '/' + str(n+1), length)
			n += 1
		if i % 2 == 0 and wayAndReturn:
			LEFT = True
		else:
			LEFT = False

	os.system("ffmpeg -framerate 30 -i " + TEMP + "/%d.png -vcodec png "+ name+".mov")


if __name__ == "__main__":
	if len(sys.argv) == 3:
		fromFolder(sys.argv[1], sys.argv[2])

	elif len(sys.argv) == 4:
		fromFolder(sys.argv[1], sys.argv[2], name=sys.argv[3])

	else:
		print("Usage: Python3 test <folder name> <temp path> <out name>(optional)")
