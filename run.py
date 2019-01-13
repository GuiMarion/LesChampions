import img
import applyToFolder
import os
import shutil
import glob

IN = "Images/"
IMAGES = IN[:-1] + '_out/'

if not os.path.exists(IMAGES):
    os.makedirs(IMAGES)

for filename in glob.glob('Images_out/*'):
	try:
	    shutil.rmtree(filename)
	except OSError as e:
	    pass	


# Construct all sorted images : run(n=256, DATA="Data/", OUT="OUT/", spaceSize=5, addData=1):
img.run(n=300, DATA = IN, OUT = IMAGES + 'images', addData=3)

# Construct videos from images
applyToFolder.main(IMAGES + 'images/', IN[:-1], length=300)