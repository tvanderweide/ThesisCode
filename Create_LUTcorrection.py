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
import scipy.optimize as opt
import os

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
        
        # ### Debayer the image
        # Potentially useful website http://answers.opencv.org/question/171179/raw-image-cvtcolor-debayer/
        # Here are all of the different conversion methods: 
        # http://mathalope.co.uk/2015/05/24/opencv-python-color-space-conversion-methods/
        
        # Debayered using the cv2 package (had to install opencv)
        color = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB).astype("uint16")
        color.shape     # __Note that the shape is now 3000 x 4000 x 3!__
    else:
        with open(filename, "rb") as rawimage:
            img = np.fromfile(rawimage, np.dtype('u2'), (4000 * 3000))
    
        if img.shape[0] != (4000 * 3000):
            raise IndexError("Resolution of the image is {}. MCC only supports processing 12MP resolution. Please reset resolution to default settings.".format(img.shape[0]))
    
        img = img.reshape((3000, 4000))
    
        # Debayered using the cv2 package (had to install opencv)
        color = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB).astype("uint16")
        color.shape
    
#    # Plot the channels of the debayered image
#    plt.matshow(color[:,:,0], cmap=plt.cm.jet); plt.show()
#    plt.matshow(color[:,:,1], cmap=plt.cm.jet); plt.show()
#    plt.matshow(color[:,:,2], cmap=plt.cm.jet); plt.show()

    return color


#####--------------------------------------------------------------------------------------------------------------------------------------------------############
# # Do the LUT fitting
# Followed an example of Guassian fitting from here:
# https://stackoverflow.com/questions/21566379/fitting-a-2d-gaussian-function-using-scipy-optimize-curve-fit-valueerror-and-m
def LUT_function( xdata, rx, ry, x0, y0, c ):
    x = xdata[0]
    y = xdata[1]
    F = np.cosh( rx*(x-x0) ) * np.cosh( ry*(y-y0) ) + c

    return F


#####--------------------------------------------------------------------------------------------------------------------------------------------------############
# Create the LUT filter to correct vignette falloff
def lut_corr(img, outfile):
    # Create x and y indices
    nrows = img.shape[0]
    ncols = img.shape[1]
    x1 = np.linspace(-0.5, 0.5, ncols,dtype="float64")
    y1 = np.linspace(-0.5, 0.5, nrows,dtype="float64")
    x, y = np.meshgrid(x1, y1)
    
    # param_names = {'rx','ry','x0','y0','c'};
    initial_guess = (2.0, 1.0, 0.0, 0.0, 0.5) #  initial parameters guess
    
    xdata = np.vstack( (x.ravel(), y.ravel()) ) # make (m*n, 2)
    
    modeled_filter_arr = np.zeros((3000,4000,3), np.float)
    # Loop over the data channels individually
    for x in range(0, 3):
        # Use real data
        data = img[:,:,x]
        data_noisy = np. true_divide( data.max(), data ) # Make the LUT filter
        ydata = data_noisy.ravel() # make (m*n, 1)
        
    #    fig, ax = plt.subplots(1, 1)
    #    ax.imshow(ydata.reshape(nrows, ncols), cmap=plt.cm.jet, origin='bottom',
    #              extent=(x.min(), x.max(), y.min(), y.max()))
    #    plt.show()
        
        popt, pcov = opt.curve_fit( LUT_function, xdata, ydata, p0=initial_guess )
    #    print(popt)
        
        # Compute the LUT function from the estimated parameters
        modeled_filter = LUT_function( xdata, *popt)
        modeled_filter = modeled_filter.reshape(nrows, ncols)
        modeled_filter_arr[:,:,x] = modeled_filter
    
    np.save(outfile, modeled_filter_arr)
    
#    # Remap to pixels from the x,y in the fitting
#    col = np.linspace(1, ncols, ncols)
#    row = np.linspace(1, nrows, nrows)
#    x, y = np.meshgrid(col, row)
    # Plot the corrections
#    fig, 
#    ax = plt.subplot(121)
#    ax.imshow(data_noisy, cmap=plt.cm.jet, origin='bottom',
#              extent=(x.min(), x.max(), y.min(), y.max()))
#    # Use modeled matrix to compute contours and plot on top of data
#    ax.contour(x, y, modeled_filter, 8, colors='w')
#    plt.show()
#    
#    # fig, 
#    ax = plt.subplot(122)
#    ax.imshow(modeled_filter, cmap=plt.cm.jet, origin='bottom',
#              extent=(x.min(), x.max(), y.min(), y.max()))
#    # Use modeled matrix to compute contours and plot on top of data
#    ax.contour(x, y, modeled_filter, 8, colors='w')
#    plt.show()
    
    return


#####-------------------------------------------------------------------------------------------------------------------------------------------------------------#####
# Average all the RAW images
def avg_Raw(fold, cam):
    # Create a list of all the RAW images
    allfiles = os.listdir(fold)
    imlist = [filename for filename in allfiles if  filename[-4:] in [".raw",".RAW"]]
    N = np.float(len(imlist))

    image = read_RAW(fold + "/" + imlist[0], cam)
    h = image.shape[0]
    w = image.shape[1]
    avg_arr = np.zeros((h,w,3), np.float)

    # Calculate the average for all images
    for img in imlist:
        im_path = fold + "/" + img
        imarr = read_RAW(im_path, cam)
        avg_arr = avg_arr + imarr/N
    
    return avg_arr


#######--------------------------------------------------------------------------------------------------------------------------------------------------------########
# Main Definition
print("Starting to create the LUT correction")
main_fold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Vignette/Version4/"


Camera_names = ['Photo_1', 'Photo_2', 'Photo_3', 'Photo_4', 'Photo_5', 'Photo_6']
for cam in Camera_names[2:]:
    print("Processing: " + cam)
    fold_name = main_fold + cam
    img_avg = avg_Raw(fold_name, cam)
    outfile = fold_name + "/lut_correction"
    lut_corr(img_avg, outfile)


