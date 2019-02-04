import numpy as np
from PIL import Image
from PIL import ImageDraw
import os
from tqdm import tqdm
from math import *
import glob
import shutil
import pygame
from pygame.locals import*


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

class img:
	def __init__(self, path, matrix = False):
		'''
		Open an image and store the matrix
		'''
		if matrix:
			self.matrix = path
			self.mymean, self.standardDeviation = self.mean()
		else:
			im = Image.open(path)
			#im = im.convert('RGB')
			self.matrix = np.array(im)
		self.length = len(self.matrix)

	def mean(self):
		'''
		Return the mean pixel of all the pixels of the matrix
		'''
		(r, v, b) = (0, 0, 0)
		(rsd, vsd, bsd) = (0, 0, 0)
		for x in range(len(self.matrix)):
			for y in range(len(self.matrix[0])):
				r += self.matrix[x][y][0]
				v += self.matrix[x][y][1]
				b += self.matrix[x][y][2]

				# For standard deviation
				rsd += self.matrix[x][y][0]**2
				vsd += self.matrix[x][y][1]**2
				bsd += self.matrix[x][y][2]**2

		r /= len(self.matrix)*len(self.matrix[0])
		v /= len(self.matrix)*len(self.matrix[0])
		b /= len(self.matrix)*len(self.matrix[0])

		rsd /= len(self.matrix)*len(self.matrix[0])
		vsd /= len(self.matrix)*len(self.matrix[0])
		bsd /= len(self.matrix)*len(self.matrix[0])

		sd = np.sqrt(rsd - r) + np.sqrt(vsd - v) +  np.sqrt(bsd - b)

		return (r, v, b), sd

	def getMatrix(self):
		return self.matrix

	def getStandardDeviation(self):
		return self.standardDeviation

	def print(self):
		for x in range(len(self.matrix)):
			print()
			for y in range(len(self.matrix[0])):
				print(self.matrix[x][y], end =" ")
		print()


	def save(self, name, polygon=True):
		if polygon:
			# read image as RGB and add alpha (transparency)
			im = Image.fromarray(self.matrix).convert("RGBA")

			# convert to numpy (for convenience)
			imArray = np.asarray(im)

			# create mask
			poly = getPolygon(3*np.pi/4, 3*np.pi/5, self.length)
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
		else:
			im = Image.fromarray(self.matrix)
			im.save(name + ".png")
			#im.save("OUT/"+ str(self.standardDeviation) + ".png")

	def computeDistance(self, val):
		'''
		Should return the distance between val et the mean of the image
		'''
		(r, v, b) = val

		m1, m2, m3 = self.mymean

		return np.sqrt((r-m1)**2 +  (v-m2)**2 + (b-m3)**2)

	def getSubSquares(self, n, addData = 1):
		'''
		Should return subsquared images of size n*n as a liste of img objects
		'''

		images = []
		for i in tqdm(range(0, len(self.matrix) // n - 1)):
			for j in range(0, len(self.matrix[0]) // n - 1):
				for k1 in range(0, n, n//addData):
					for k2 in range(0, n, n//addData):
						im = img(self.matrix[i*n + k1 : (i+1)*n + k1, j*n + k2 : (j+1)*n + k2], matrix = True)
						#if im.getStandardDeviation() < 530:
						images.append(im)

		return images

	def findClosestPoint(self, space):
		dist =  100000
		for elem in space:
			distTemp = self.computeDistance(elem)
			if distTemp <= dist:
				dist = distTemp
				returnedValue = elem

		return returnedValue

def constructDataBase(path, n, addData = 0):
	'''
	Open all the files from the path and return a list of all the resulting subsquares
	'''

	files = [os.path.join(path, f) for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f != ".DS_Store")]

	images = []

	for file in files:
		print(file)
		images.extend(img(file).getSubSquares(n, addData = addData))

	return images

def sortImages(images, OUT, spaceSize = 5):
	'''
	For each image in images, find the closest point of the dicretized space and save the image in the directory with the name of this point
	'''
	space = discretizeSpace(spaceSize)

	dico = {}
	k = 0
	for image in tqdm(images):

		point = image.findClosestPoint(space)
		if point not in dico:
			dico[point] = []
		dico[point].append(k)
		k += 1

	if not os.path.exists(OUT):
	    os.makedirs(OUT)

	i = 0
	for key in dico:
		for elem in dico[key]:
			images[elem].save(OUT + "/" + '0'*(4-len(str(i))) + str(i))
			i += 1


def discretizeSpace(n):
	'''
	Return n^3 points equaly distributed in the pixel space (0, 0, 0) -> (255, 255, 255)
	'''

	points = []

	for r in range(n):
		for v in range(n):
			for b in range(n):
				points.append((r*255//n + 255//(2*n), v*255//n + 255//(2*n), b*255//n + 255//(2*n)))

	return points


def filterDataBase(database):
	databaseout = []
	pygame.init()
	ecran = pygame.display.set_mode((700, 700))
	continuer = True
	print("You will process", len(database), "images.")

	k = 0

	while continuer:

		try :
			database[k].save(".tmp", polygon=False)
			image = pygame.image.load(".tmp.png").convert_alpha()
		except pygame.error:
			print("Error with", database[k])
			k += 1

		ecran.fill((0,0,0))
		ecran.blit(image, (50, 50))                       
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					continuer = False
				elif event.key == K_UP or event.key == K_RIGHT:
					databaseout.append(database[k])
					k += 1
				elif event.key == K_DOWN:
					k += 1

		if k >= len(database):
			continuer = False


	pygame.quit()

	return databaseout


def run(n=256, DATA="Data/", OUT="OUT/", spaceSize=5, addData=1, filter=True):

	for filename in glob.glob('Images_out/images'):
		try:
		    shutil.rmtree(filename)
		except OSError as e:
		    pass	
	    
	data = constructDataBase(DATA, n, addData = addData)

	data = filterDataBase(data)
	print("You selected", len(data), "images.")

	sortImages(data, OUT, spaceSize)
