import numpy
from PIL import Image
import os
import glob
from tqdm import tqdm

def resizeFile(name, outSize, outName):
	temp = Image.open(name)
	temp = temp.resize((outSize, outSize))
	temp.save(outName)

def resizeFolder(Folder, outFolder, outSize):

	if outFolder[-1] != "/":
		outFolder += "/"

	print("____ Resizing ...")

	if not os.path.exists(outFolder):
	    os.makedirs(outFolder)

	for file in tqdm(glob.glob(Folder + "/*")) :
		if os.path.exists(outFolder + file[file.rfind("/")+1:]):
			print("The file", file, "already exists in the output folder, we quit the program.")
			quit()
		resizeFile(file, outSize, outFolder + file[file.rfind("/")+1:])

	print("Resizing finished.")