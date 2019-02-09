import glob
import os
import sys

def main(Folder, start):
	
	for file in glob.glob(Folder + "*.png"):
		os.rename(file, file[:file.rfind("/")+1] + '0'*(4-len(str(start))) + str(start) + ".png")
		start += 1		

if __name__ == "__main__":

	if len(sys.argv) == 3 :
		main(sys.argv[1], int(sys.argv[2]))

	else:
		print("Usage: Python3 rename.py <folder> <starting int value>")  


