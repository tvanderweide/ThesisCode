# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 11:03:13 2018

Correct drone image EXIF data

@author: thomasvanderweide
"""

import exiftool
import glob

def get_metadata(fn):
    with exiftool.ExifTool("C:/Users/ThomasVanDerWeide/Downloads/exiftool-10.60/exiftool(-k).exe") as et:
        metadata = et.get_metadata(fn)
    metadata2 = metadata
    metadata = None
    return metadata2

def updateMetaData(files):
    with exiftool.ExifTool("C:/Users/ThomasVanDerWeide/Downloads/exiftool-10.60/exiftool(-k).exe") as et:
        for file in files:
            pic = file.encode()
            et.execute(b"-GPSAltitude=40", pic)
#    for d in metadata:
#        d['EXIF:GPSAltitude'] = 40
#        et.execute('-EXIF:GPSAltitude' = 40, files)
        
    with exiftool.ExifTool("C:/Users/ThomasVanDerWeide/Downloads/exiftool-10.60/exiftool(-k).exe") as et:
        metadata2 = et.get_metadata_batch(files)
    for d in metadata2:
        print(d['EXIF:GPSAltitude'])


def iterFolders(fn):
    files = []
#    for folder in sorted(glob.iglob(fn + "*")):
#        files = []
    for jpg in sorted(glob.iglob(fn + "/*.tif")):
        files.append(jpg)
    print("Number of files: " + str(len(files)))
    updateMetaData(files)
        
        

############--------------------------------------------------------------------------------------------------------------------------############
# Update the image metadata to have the correct elevation in meters
elev = 40

fold = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Drone/Western - Copy/6-12-2018/Processed_1/vigCorrected/"
#fold = "H:/Terroir/Bitner/photo/Processed_1/vigCorrected/"

iterFolders(fold)