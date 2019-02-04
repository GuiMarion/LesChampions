import pygame
from pygame.locals import*
from glob import glob
import os
from optparse import OptionParser

def main(folder="FACES/", k=0):
	pygame.init()

	ecran = pygame.display.set_mode((700, 700))

	continuer = True

	images = glob(folder+"*.png") 

	print("You will process", len(images), "images.")

	n = k - 1

	while continuer:

		try :
			image = pygame.image.load(images[k]).convert_alpha()
		except pygame.error:
			print("You should start at index", n)
			k += 1
			n += 1

		ecran.fill((0,0,0))
		ecran.blit(image, (50, 50))                       
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == K_ESCAPE:
					continuer = False
				elif event.key == K_UP or event.key == K_RIGHT:
					k += 1
					n += 1
				elif event.key == K_LEFT:
					k -= 1
					n -= 1
				elif event.key == K_DOWN:
					os.remove(images[k])
					k += 1
					n += 1

		if k >= len(images):
			continuer = False


	pygame.quit()

	print("You should start at index", n)



if __name__ == "__main__":

	usage = "usage: %prog [options] <path to folder> <starting indice -optional>"
	parser = OptionParser(usage)

	parser.add_option("-k", "--start_k", type="int",
					  help="Starting index", 
					  dest="k", default=0)

	options, arguments = parser.parse_args()
	
	if len(arguments) == 1:
		main(folder=arguments[0])
	elif len(arguments) == 2:
		main(folder=arguments[0], k=int(arguments[1]))

	else:
		parser.error("Invalid options.")
