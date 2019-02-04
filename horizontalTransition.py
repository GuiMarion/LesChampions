from PIL import Image
import numpy as np
import os, sys
import glob
from random import shuffle
import random
from tqdm import tqdm
from math import *
from PIL import ImageDraw
import matplotlib.pyplot as plt

def getSigma(x):
	#return np.sin(0.005*x + 300)*8 + 8
	if x > 4150:
		return np.sin(0.003*x + 294)*8 + 8
	else: 
		return 0

def plotSigma(save=""):
	X = np.arange(5820)
	Y = []
	for i in range(len(X)):
		Y.append(getSigma(i))

	plt.plot(X/30, Y)
	plt.xlabel("Temps en secondes")
	plt.ylabel("Valeur de Sigma")
	
	if save != "":
		plt.savefig(save)

	plt.show()


def getEpochs(x):
	if x < 405:
		return 180
	else:
		return np.sin(0.0028*x + 802.35)*35 + 8 + 195

def plotEpochs(save=""):
	X = np.arange(5820)
	Y = []
	for i in range(len(X)):
		Y.append(getEpochs(i))

	plt.plot(X/30, Y)
	plt.xlabel("Temps en secondes")
	plt.ylabel("Lenteur")
	
	if save != "":
		plt.savefig(save)

	plt.show()

def getmuPause(x):
	if x < 500:
		mu = (0.33 - (0.001*x**3)/(0.001*5820**3)*300)*1000
		return 120
	elif x >= 500 :
		return np.sin(0.005*x + 801.8)*15  + 120

def getPpause(x):
	if x < 500:
		mu = getmuPause(x)
		sigma = mu*0.1
		return 2*int(np.random.normal(mu, sigma, 1)[0])
	elif x >= 500 :
		mu = getmuPause(x)
		sigma = mu*0.35
		return int(np.random.normal(mu, sigma, 1)[0])

def plotPause(save=""):
	X = np.arange(5820)
	Y = []
	for x in X:
		Y.append(getmuPause(x))
	plt.plot(X/30, Y)
	plt.xlabel("Temps en secondes")
	plt.ylabel("Temps de pause moyen")
	if save != "":
		plt.savefig(save)

	plt.show()

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


def fromFolder(FOLDER, TEMP, N = 1000, EPOCHS = 150, transitionWidth = 100, name="test", wayAndReturn = True, length=300, seed=0):

	np.random.seed(seed)
	
	sigma = 0

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

		#EPOCHS = int(getEpochs(n))
		for k in range(0, EPOCHS):
			sigma = getSigma(n)
			for p in range(s*k, s*(k+1)):
				if LEFT :
					(elem, L) = generatePixel((k*len(L))//(EPOCHS), sigma, L, LEFT = True)
				else:
					(elem, L) = generatePixel(((len(L)*EPOCHS - k*len(L)))//(EPOCHS), sigma, L)
				im1.putpixel(elem, im2.getpixel(elem))

			im1.save(TEMP + '/' +str(n+1) + ".png")
			#saveAsPolygon(im1, TEMP + '/' + str(n+1), length)
			n += 1
		pause = getPpause(n)
		while pause > 0:
			im1.save(TEMP + '/' +str(n+1) + ".png")
			n += 1
			pause -= 1

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
