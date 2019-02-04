import horizontalTransition
from os import listdir
from os.path import isfile, join
from shutil import copyfile
import sys
import os
import shutil
import time

N = 24


def main(mypath, name, length=300, VideoOUT="OUT/"):
	files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

	OUT = name+"_out/"
	SUB = OUT + "temp_sub/"

	if not os.path.exists(OUT):
		os.makedirs(OUT)

	if not os.path.exists(VideoOUT):
		os.makedirs(VideoOUT)

	if not os.path.exists(SUB):
		os.makedirs(SUB)
	else:
		shutil.rmtree(SUB)
		os.makedirs(SUB)


	Files = []
	temp = []
	if not os.path.exists(SUB + str(0)):
		os.makedirs(SUB + str(0))

	for i in range(len(files)):
		#if i % (len(files)//N) == 0:
			#Files.append(temp)
			#temp = [] 
		if not os.path.exists(SUB + str(i%N)):
			os.makedirs(SUB + str(i%N))

		temp.append(files[i])
		copyfile(mypath + "/" + files[i], SUB + str(i % N) + "/" + files[i])


	folders = [f for f in listdir(SUB) if not isfile(join(SUB, f))]

	k = 0
	for folder in folders:
		print(folder)
		horizontalTransition.fromFolder(SUB + folder, OUT + 'temp',  name = VideoOUT+ str(folder), length=300, seed=k)
		k += 1


if __name__ == "__main__":
	if len(sys.argv) == 2:
		main(sys.argv[1])

	elif len(sys.argv) == 3:
		main(sys.argv[1], name=sys.argv[2])

	else:
		print("Usage: Python3 test <folder name> <out name>(optional)")
