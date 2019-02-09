import img
import applyToFolder
import resize

import os
import shutil
import glob

IN = "Images/"
IMAGES = IN[:-1] + '_out/'

if not os.path.exists(IMAGES):
    os.makedirs(IMAGES)

# Construct all sorted images : run(n=256, DATA="Data/", OUT="OUT/", spaceSize=5, addData=1):
#img.run(n=600, DATA = IN, OUT = IMAGES + 'images', addData=3)

# Resizing the images
resize.resizeFolder("polygons/", IMAGES + 'images/', 150)
# Construct videos from images
applyToFolder.main(IMAGES + 'images/', IN[:-1], length=300, VideoOUT="OUT2/")