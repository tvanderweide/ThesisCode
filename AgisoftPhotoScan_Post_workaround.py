# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 10:42:48 2018

@author: thomasvanderweide
"""

import subprocess
import glob
import os

#####-----------------------------------------------------------------------------------------------------------------------------------#######
def crop_ortho(sf, fn):
    import fiona
    import rasterio
    from rasterio.mask import mask
    # Open the shapefile
    with fiona.open(sf, "r") as shapefile:
        geoms = [feature["geometry"] for feature in shapefile]
    
    # Read in the Tif
    with rasterio.open(fn) as src:
        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
           
    # Update Metadata
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    
    # Cropped TIF name
    maskedFN = fn.rpartition(".")[0] + "_masked.tif"
    # Save the Cropped TIF
    with rasterio.open(maskedFN, "w", **out_meta) as dest:
        dest.write(out_image)

    print("Finished cropping the orthomosaic.")

    return


def iter_folder(fn):
    
    for day in sorted(glob.iglob(fn + "*")):
        print(day)
        Processed = day + "/Processed_2/"
        vigCorrFold = Processed + "vigCorrected/"
        calibratedFold = vigCorrFold + "calibrated/"
        # Create a list of all the previously organized files
        
    
    
#    crop_ortho(sf, ortho)
#    crop_ortho(sf, ortho_NDVI)
    
    return


#####-----------------------------------------------------------------------------------------------------------------------------------#######
# Run the main code
print("Starting Program...")

fn = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Drone/Hartman - Copy/"

iter_folder(fn)
