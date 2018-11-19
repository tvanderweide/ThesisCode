#!/usr/bin/env python
# coding: utf-8
# RAW image testing in Python following MAPIR_Processing_dockwidget.py
# Save RAW Images as TIFFs
# Apply vignette correction to all drone imagery

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
    modpath = 'N:/Data02/projects-active/IGEM_Kairosys/exiftool-11.12/'
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
def read_RAW(fn):
    # Choose the filename you want to load
    filename= fn

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
def iter_fold(fold, vigArr, field):
    # Seperate the Vignette Correction into appropriate bands
    R, G, B = 0, 1, 2
    blueVig = vigArr[:,:,B]
    greenVig = vigArr[:,:,G]
    NIRVig = vigArr[:,:,R]
    
    if field == "Hartman - Copy":
        for day in sorted(glob.iglob(fold + "*")):
            Processed = day + "/Processed_1/"
            # Create a list of all the previously organized files
            allfiles = os.listdir(Processed)
            for entry in allfiles:
                if entry[:2] == "Th":
                    allfiles.remove(entry)
            imlist = []
            for flight in allfiles:
                findFiles = os.listdir(Processed + flight)
                imlist = [filename for filename in findFiles if filename[-4:] in [".tif",".TIF"]]
            N = np.int(len(imlist))
            print("There are " + str(N) + " images to process...")
            imList = [w[:-4] + w[-4:].replace('.tif', '.RAW') for w in imlist]
        
            # Create folder to save TIFFs if it DNE
            outFold = day + "/Processed_2/"
            if not os.path.exists(outFold):
                os.mkdir(outFold)
            
            # Create a list of the JPG Images
            inJPG = day + "/*.JPG"
            JPG = []
            for jpgfn in sorted(glob.iglob(inJPG)):
                JPG.append(jpgfn)  
                
            # Create folder to save vignette corrected TIFFs if it DNE
            outFold2 = day + "/Processed_2/vigCorrected/"
            if not os.path.exists(outFold2):
                os.mkdir(outFold2)
        
            # Save RAW images as TIFF files
            inFold = day + "/*.RAW"
            for img in sorted(glob.iglob(inFold)):
                imgPart = img.rpartition("\\")[2]
                if imgPart in imList:
                    imarr = read_RAW(img)
                        
                    # Save the 16-bit images
                    imgName = img.rpartition("\\")[2].rpartition(".")[0]
                    outphoto = outFold + imgName + ".tif"
                    io.imsave(outphoto, imarr)
                    print("Saved: " + img)
                    
                    # Transfer the Metadata
                    for jpgimg in JPG:
                        jpgName = int(jpgimg.rpartition("\\")[2].rpartition("_")[2].rpartition(".")[0]) - 1
                        rawName = int(img.rpartition("\\")[2].rpartition("_")[2].rpartition(".")[0])
                        if jpgName == rawName:
                            print("Found Match: " + str(jpgName) + " with " + str(rawName))
                            copyExif(jpgimg, outphoto)
                            break  
                    
                    # Apply the Vignette correction
                    # Split into bands
                    Blue = np.copy(imarr[:,:,B])
                    Green = np.copy(imarr[:,:,G])
                    NIR = np.copy(imarr[:,:,R])
                    
                    # Apply the vignette corretion 
                    blueArray = np.multiply(Blue, blueVig)
                    greenArray = np.multiply(Green, greenVig)
                    NIRArray = np.multiply(NIR, NIRVig)
                
                    # Convert to 3000 x 4000 x 3 array
                    arr = np.zeros(imarr.shape, dtype = np.uint16)
                    arr[:,:,R] = NIRArray.astype(np.uint16)
                    arr[:,:,G] = greenArray.astype(np.uint16)
                    arr[:,:,B] = blueArray.astype(np.uint16)
                
                    # Save the 16-bit images
                    outphoto2 = outFold2 + imgName + ".tif"
                    io.imsave(outphoto2, arr)
                    
                    # Transfer the Metadata
                    copyExif(outphoto, outphoto2)
    elif field == "Western - Copy":
        for day in sorted(glob.iglob(fold + "*"))[-2:]:
#            print(day)
            Processed = day + "/Processed_1/"
            # Create a list of all the previously organized files
            imlist = []
            findFiles = os.listdir(Processed + "vigCorrected/")
            imlist = [filename for filename in findFiles if filename[-4:] in [".tif",".TIF"]]
            N = np.int(len(imlist))
            print("There are " + str(N) + " images to process...")
            imList = [w[:-4] + w[-4:].replace('.tif', '.RAW') for w in imlist]
        
            # Create folder to save TIFFs if it DNE
            outFold = day + "/Processed_2/"
            if not os.path.exists(outFold):
                os.mkdir(outFold)
            
            # Create a list of the JPG Images
            inJPG = day + "/*.JPG"
            JPG = []
            for jpgfn in sorted(glob.iglob(inJPG)):
                JPG.append(jpgfn)  
                
            # Create folder to save vignette corrected TIFFs if it DNE
            outFold2 = day + "/Processed_2/vigCorrected/"
            if not os.path.exists(outFold2):
                os.mkdir(outFold2)
        
            # Save RAW images as TIFF files
            inFold = day + "/*.RAW"
            for img in sorted(glob.iglob(inFold)):
                imgPart = img.rpartition("\\")[2]
                if imgPart in imList:
                    imarr = read_RAW(img)
                        
                    # Save the 16-bit images
                    imgName = img.rpartition("\\")[2].rpartition(".")[0]
                    outphoto = outFold + imgName + ".tif"
                    io.imsave(outphoto, imarr)
                    print("Saved: " + img)
                    
                    # Transfer the Metadata
                    for jpgimg in JPG:
                        jpgName = int(jpgimg.rpartition("\\")[2].rpartition("_")[2].rpartition(".")[0]) - 1
                        rawName = int(img.rpartition("\\")[2].rpartition("_")[2].rpartition(".")[0])
                        if jpgName == rawName:
                            print("Found Match: " + str(jpgName) + " with " + str(rawName))
                            copyExif(jpgimg, outphoto)
                            break  
                    
                    # Apply the Vignette correction
                    # Split into bands
                    Blue = np.copy(imarr[:,:,B])
                    Green = np.copy(imarr[:,:,G])
                    NIR = np.copy(imarr[:,:,R])
                    
                    # Apply the vignette corretion 
                    blueArray = np.multiply(Blue, blueVig)
                    greenArray = np.multiply(Green, greenVig)
                    NIRArray = np.multiply(NIR, NIRVig)
                
                    # Convert to 3000 x 4000 x 3 array
                    arr = np.zeros(imarr.shape, dtype = np.uint16)
                    arr[:,:,R] = NIRArray.astype(np.uint16)
                    arr[:,:,G] = greenArray.astype(np.uint16)
                    arr[:,:,B] = blueArray.astype(np.uint16)
                
                    # Save the 16-bit images
                    outphoto2 = outFold2 + imgName + ".tif"
                    io.imsave(outphoto2, arr)
                    
                    # Transfer the Metadata
                    copyExif(outphoto, outphoto2)
    else:
        print("Field not recognized")
    return


#######--------------------------------------------------------------------------------------------------------------------------------------------------------########
# Main Definition
print("Running Convert RAW script...")
field = "Western - Copy"
DataFold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Drone/" + field + "/"
vigCorr = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Vignette/Version4/Photo_1"

VigArr = loadVignette(vigCorr)
iter_fold(DataFold, VigArr, field)




