# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 10:42:48 2018


Run script in headless mode (without opening Agisoft) from command line (or python script)
 photoscan.exe -r <script.py>
 
 
@author: thomasvanderweide
"""

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


#####-----------------------------------------------------------------------------------------------------------------------------------#######
def iter_folder(field):
            
    for fn in field:
        for day in sorted(glob.iglob(fn + "*")):
            if fn.rpartition("Isolated/")[2].rpartition("/")[0] == "Hartman":
                fieldNum = ["2A", "2B"]
                for fieldID in fieldNum:
                    dayfold = day.replace("\\","/")
                    proj = fieldID
                    processday = dayfold + "/" + proj + "/"
                    save_orthoFold = processday + "orhto/"
                    onlyfiles = [f for f in os.listdir(save_orthoFold)]
                    if len(onlyfiles) >= 1:
                        projname = fn.rpartition("Isolated/")[2].rpartition("/")[0].replace("/","-")
                        ortho_img = save_orthoFold + projname + ".tif"
                        ortho_NDVI = save_orthoFold + projname + "_NDVI.tif"
                        
                        #Define the 
                        shapefile = "C:/Users/thomasvanderweide/Documents/Shapefiles/"
                        sf = shapefile + fn.rpartition("/")[0].rpartition("/")[2] + processday.rpartition("18/")[2].rpartition("/")[0] + ".shp"
                        print(sf)
                        # Crop the orthomosaic Images
                        crop_ortho(sf, ortho_img)
                        if len(onlyfiles) >= 2:
                            crop_ortho(sf, ortho_NDVI)
                            
            if fn.rpartition("Isolated/")[2].rpartition("/")[0] == "Western":
                fieldNum = ["1A", "1B"]
                for fieldID in fieldNum:
                    dayfold = day.replace("\\","/")
                    proj = fieldID
                    processday = dayfold + "/" + proj + "/"
                    save_orthoFold = processday + "orhto/"
                    onlyfiles = [f for f in os.listdir(save_orthoFold)]
                    if len(onlyfiles) >= 1:
                        projname = fn.rpartition("Isolated/")[2].rpartition("/")[0].replace("/","-")
                        ortho_img = save_orthoFold + projname + ".tif"
                        ortho_NDVI = save_orthoFold + projname + "_NDVI.tif"
                        
                        #Define the 
                        shapefile = "C:/Users/thomasvanderweide/Documents/Shapefiles/"
                        sf = shapefile + fn.rpartition("/")[0].rpartition("/")[2] + processday.rpartition("18/")[2].rpartition("/")[0] + ".shp"
                        print(sf)
                        # Crop the orthomosaic Images
                        crop_ortho(sf, ortho_img)
                        if len(onlyfiles) >= 2:
                            crop_ortho(sf, ortho_NDVI)
    
    return


#####-----------------------------------------------------------------------------------------------------------------------------------#######
# Run the main code
print("Starting Program...")

field = ["C:/Users/thomasvanderweide/Documents/Isolated/Hartman/", 
      "C:/Users/thomasvanderweide/Documents/Isolated/Western/"]

iter_folder(field)
    