# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 13:07:10 2018

@author: thomasvanderweide
"""

import fiona
import rasterio
from rasterio.mask import mask
        

#####-----------------------------------------------------------------------------------------------------------------------------------#######
def crop_ortho(sf, fn):
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


#####-----------------------------------------------------------------------------------------------------------------------------------#######
# Run the main code
print("Starting to crop the orthomosaic")

ortho = "H:/Terroir/Bitner/photo/Processed_1/vigCorrected/BitnerOrtho1.tif"
ortho_NDVI = ortho.rpartition(".")[0] + "_NDVI.tif"

# Shape file location
sf = "H:/Terroir/Bitner/Bitner.shp"

crop_ortho(sf, ortho)
crop_ortho(sf, ortho_NDVI)