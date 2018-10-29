#!/usr/bin/env python
# coding: utf-8
# RAW image testing in Python following MAPIR_Processing_dockwidget.py
# Save RAW Images as TIFFs
# Apply vignette correction to all fields

# Import required libraries
import numpy as np
import copy
import matplotlib.pyplot as plt
import cv2
from skimage import io
import os
import subprocess
import glob


#####-----------------------------------------------------------------------------------------------------------------------------------------------######
def copyExif(inphoto, outphoto):
    modpath = 'H:/Terroir/Code/exiftool-11.12/'
    #si = subprocess.STARTUPINFO()
    exifout = subprocess.run(
    [modpath + r'exiftool(-k).exe', #r'-config', modpath + os.sep + r'mapir.config',
    r'-overwrite_original_in_place', r'-tagsFromFile',
    os.path.abspath(inphoto), r'-all:all<all:all', os.path.abspath(outphoto)], 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).stderr.decode("utf-8")
    
    
#####-----------------------------------------------------------------------------------------------------------------------------------------------######
def loadVignette(vigFolder):
    # Read in the vignette correciton
    vigFn = vigFolder + "/lut_correction.npy"
    mat = np.load(vigFn)
    return mat

#####-----------------------------------------------------------------------------------------------------------------------------------------------######
# Read in RAW files
def read_RAW(fn, cam):
    # Choose the filename you want to load
#    filename = './Version4/Photo_2/2018_0925_234508_021.RAW'
    filename= fn
    if cam in ['Photo_1', 'Photo_2', 'Photo_5', 'Photo_6']:
        data = np.fromfile( filename, dtype=np.uint8 ) # read at uint8
        data = np.unpackbits( data ) # convert to binary bits
        datsize = data.shape[0]
        data = data.reshape( ( int(datsize / 4), 4 ) ) # map to 4 bit rows
        
        
        # Here is where rearrange the data
        temp  = copy.deepcopy(data[0::2]) # grab every other byte from 0 to npts-1 
        temp2 = copy.deepcopy(data[1::2]) # grab every other byte from 1 to npts-1
        
        # flip every other bit
        data[0::2] = temp2
        data[1::2] = temp
        
        # Now create a 16-bit number and reshape into a single array; then write to bytes  
        udata = np.packbits(np.concatenate([data[0::3], np.array([0, 0, 0, 0] * 12000000, dtype=np.uint8).reshape(12000000,4), data[2::3], data[1::3]], axis=1).reshape(192000000, 1)).tobytes()
        
        # Read the bits -- 'u2' is a uint16 number; and reshape to image
        img = np.frombuffer( udata, np.dtype('u2'), (4000*3000) ).reshape((3000, 4000))
        
    #    # Plot the RAW data (3000,4000); note this has not yet been debayered
    #    plt.matshow(img, cmap=plt.cm.jet)
    #    plt.show()
        
    else:
        with open(filename, "rb") as rawimage:
            img = np.fromfile(rawimage, np.dtype('u2'), (4000 * 3000))
    
        if img.shape[0] != (4000 * 3000):
            raise IndexError("Resolution of the image is {}. MCC only supports processing 12MP resolution. Please reset resolution to default settings.".format(img.shape[0]))
    
        img = img.reshape((3000, 4000))
    
    ### Debayer the image
    # Potentially useful website http://answers.opencv.org/question/171179/raw-image-cvtcolor-debayer/
    # Here are all of the different conversion methods: 
    # http://mathalope.co.uk/2015/05/24/opencv-python-color-space-conversion-methods/
    # Debayered using the cv2 package (had to install opencv)
    color = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB).astype("uint16")
    color.shape
    
#    # Plot the channels of the debayered image
#    plt.matshow(color[:,:,0], cmap=plt.cm.jet); plt.show()
#    plt.matshow(color[:,:,1], cmap=plt.cm.jet); plt.show()
#    plt.matshow(color[:,:,2], cmap=plt.cm.jet); plt.show()

    return color


#######--------------------------------------------------------------------------------------------------------------------------------------------------------########
def applyVignette(fn1, vigArr):
    print("Apply Vignette to TIF in: " + fn1)
    # Seperate the Vignette Correction into appropriate bands
    R, G, B = 0, 1, 2
    blueVig = vigArr[:,:,B]
    greenVig = vigArr[:,:,G]
    NIRVig = vigArr[:,:,R]
    
    # Create Vig Corrected folder if it DNE
    outFold = fn1 + "vigCorrected/"
    if not os.path.exists(outFold):
        os.mkdir(outFold)
        
    infold = fn1 + "*.tif"
    # Apply the vignette correction to all TIF images
    for img in sorted(glob.iglob(infold)):
        print("Processing: " + img)
        imgName = img.rpartition("\\")[2]
        # Read in the JPG images
        im = io.imread(img)
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
        
        # Save the 16-bit images
        outphoto = outFold + imgName
        io.imsave(outphoto, arr)
        
        # Transfer the Metadata
        copyExif(img, outphoto)
    return


#######--------------------------------------------------------------------------------------------------------------------------------------------------------########
def saveTIF(fieldFolder, vigFolder, cam):
    fieldFolder = fieldFolder + "/"
    print("Converting RAW to TIFF in: " + fieldFolder)
    # Create folder to save TIFFs if it DNE
    fn1 = fieldFolder + "/Processed_2/"
    if not os.path.exists(fn1):
        os.mkdir(fn1)
    
    inJPG = fieldFolder + "/*.JPG"
    JPG = []
    for jpgfn in sorted(glob.iglob(inJPG)):
        JPG.append(jpgfn)
    
    print(JPG)
    # Save RAW images as TIFF files
    inFold = fieldFolder + "/*.RAW"
    for img in sorted(glob.iglob(inFold)):
        imarr = read_RAW(img, cam)
            
        # Save the 16-bit images
        imgName = img.rpartition("\\")[2].rpartition(".")[0]
        outphoto = fn1 + imgName + ".tif"
        io.imsave(outphoto, imarr)
        print("Saved: " + imgName)
        
        # Transfer the Metadata
        for jpgimg in JPG:
            jpgName = jpgimg.rpartition("\\")[2].rpartition("_")[0]
            rawName = imgName.rpartition("_")[0]
            if jpgName == rawName:
                print("JPG: " + jpgimg)
                print("TIF: " + img)
                copyExif(jpgimg, outphoto)
                break  
    
    return fn1


#######--------------------------------------------------------------------------------------------------------------------------------------------------------########
# Main Definition
print("Running Covert RAW script...")
fieldFold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Fieldsv3/"
vigFold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Vignette/Version4/"

possibleCams = ["Field1A", "Field1B", "Field2A", "Field2B"]
possibleVig = ["Photo_3", "Photo_2","Photo_4","Photo_5"]
for fieldNum in range(0,4):
    fieldName = possibleCams[fieldNum]
    vigName = possibleVig[fieldNum]
    
    fieldFolder = fieldFold + fieldName
    vigFolder = vigFold + vigName
    
    fn1 = saveTIF(fieldFolder, vigFolder, fieldName)

    VigArr = loadVignette(vigFolder)
    applyVignette(fn1, VigArr)



