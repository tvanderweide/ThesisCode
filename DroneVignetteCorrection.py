# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 14:01:48 2018

Appy Vignette Correction to Survey3
v2
For Drone Imagery
v3
Transfer Metadata











NOT USED, but close to the code that was









@author: thomasvanderweide
"""

import os
import glob
import numpy as np
from skimage import io
import scipy.io as sio
import scipy.misc
import subprocess

def copyExif(inphoto, outphoto):
    modpath = 'H:/Terroir/Code/exiftool-11.12/'
    #si = subprocess.STARTUPINFO()
    exifout = subprocess.run(
    [modpath + r'exiftool(-k).exe', #r'-config', modpath + os.sep + r'mapir.config',
    r'-overwrite_original_in_place', r'-tagsFromFile',
    os.path.abspath(inphoto), r'-all:all<all:all', os.path.abspath(outphoto)], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).stderr.decode("utf-8")
#    print(exifout)
    
def loadVignette(vigFolder):
    # Read in the vignette correciton
    vigFn = vigFolder + "lut_corrections_tif_modeled.mat"
    mat = sio.loadmat(vigFn)
    return mat

def applyVignette(dataFold, vigArr, outFold):
    # Seperate the Vignette Correction into appropriate bands
    R, G, B = 0, 1, 2
    blueVig = vigArr['lut_B']
    greenVig = vigArr['lut_G']
    NIRVig = vigArr['lut_NIR']
    
    # Iterate through all the fields
#    for day in os.listdir(dataFold):
    fn1 = dataFold # + "/Processed_1/"
#    fn1 = os.path.join(dataFold, fn)
    # Create Vig Corrected folder if it DNE
    outFold = fn1 + "vigCorrected/"
    if not os.path.exists(outFold):
        os.mkdir(outFold)
        
#    for flight in os.listdir(fn1):
#        fn2 = os.path.join(fn1, flight)
#            print(fn2)
#    if (os.path.isdir(fn2) and (fn2.rpartition('/')[2][0] == "F")):
    infold = fn1 + "/*.jpg"
    # Apply the vignette correction to all TIF images
    for jpg in sorted(glob.iglob(infold)):
        print("Processing: " + jpg)
        jpgName = jpg.rpartition("\\")[2]
        # Read in the JPG images
        im = io.imread(jpg)
        # Load the bands        
        Blue = np.copy(im[:,:,B])
        Green = np.copy(im[:,:,G])
        NIR = np.copy(im[:,:,R])
       
        # Apply the vignette corretion 
        blueArray = np.multiply(Blue, blueVig)
        greenArray = np.multiply(Green, greenVig)
        NIRArray = np.multiply(NIR, NIRVig)
        
        
        # Convert to 3000 x 4000 x 3 array
        arr = np.zeros(im.shape, dtype = np.uint16)
        arr[:,:,R] = NIRArray.astype(np.uint16)
        arr[:,:,G] = greenArray.astype(np.uint16)
        arr[:,:,B] = blueArray.astype(np.uint16)
                
        # Save the 8-bit images
        outphoto = outFold + jpgName
        scipy.misc.toimage(arr).save(outphoto)
        # Transfer the Metadata
        copyExif(jpg, outphoto)
    return arr


############-----------------------------------------------------------------------------------------------------------------------------#########
# Read in and apply vignette correction to the desired images

dataFold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Drone/Western - Copy/7-14-2018/"
vigFold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Vignette/Version4/Photo_1/Processed_1/"

outFold = dataFold + "/vigCorrected1/"
if not os.path.exists(outFold):
    os.mkdir(outFold)

VigArr = loadVignette(vigFold)
imgArr = applyVignette(dataFold, VigArr, outFold)




























