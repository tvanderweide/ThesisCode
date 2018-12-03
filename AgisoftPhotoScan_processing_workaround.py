'''
Auto batch process for Agisoft Photoscan
 Processes all tif images into an orthomosaic

12/2/2018
Made to run thru Photoscan
 
  
References
 https://lastexiler.wordpress.com/2017/02/22/auto-batch-processing-code-for-photoscan/
 https://mapbox.s3.amazonaws.com/playground/perrygeo/rasterio-docs/cookbook.html
'''
import PhotoScan
import os, re, time, sys, glob


#####-----------------------------------------------------------------------------------------------------------------------------------#######
## get the photo (.tif) list in specified folder
def getPhotoList(root_path, photoList):
    pattern = '.tif$'
    for root, dirs, files in os.walk(root_path):
        for name in files:
            if re.search(pattern,name):
                cur_path = os.path.join(root, name)
                #print (cur_path)
                photoList.append(cur_path)
    return


#####-----------------------------------------------------------------------------------------------------------------------------------#######
## Batch Process Images in Agisoft Photoscan
def photoscanProcess(img_path, save_file, save_ortho, VI_flag, quality):
    if quality == "Highest":
        matchaccuracy = PhotoScan.HighestAccuracy
        depthquality = PhotoScan.UltraQuality
    elif quality == "High":
        matchaccuracy = PhotoScan.HighAccuracy
        depthquality = PhotoScan.HighQuality
    elif quality == "Low":
        matchaccuracy = PhotoScan.LowAccuracy
        depthquality = PhotoScan.LowQuality
    elif quality == "Lowest":
        matchaccuracy = PhotoScan.LowestAccuracy
        depthquality = PhotoScan.LowestQuality
    else:
        matchaccuracy = PhotoScan.MediumAccuracy
        depthquality = PhotoScan.MediumQuality
            
    # Clear the Console
    PhotoScan.app.console.clear()
     
    ## construct the document class
    doc = PhotoScan.app.document
    
    ## save project
    doc.save( save_file )
    print ('&amp;gt;&amp;gt; Saved to: ' + save_file)
    ## add a new chunk
    chunk = doc.addChunk()
    
#    ## Re-run in current document
#    doc.open(psxfile)
#    chunk = doc.chunk
    
    ## set coordinate system
    chunk.crs = PhotoScan.CoordinateSystem("EPSG::4326") # WGS84
    
    ################################################################################################
    ### Photo List ###
    photoList = []
    getPhotoList(img_path, photoList)
    # Add photos to list
    chunk.addPhotos(photoList)
    
    ################################################################################################
    ### Align Photos ###
    ## Perform image matching for the chunk frame.
    # matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000[, progress])
    # - Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy]
    # - Reference Preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
    
    chunk.matchPhotos(accuracy = matchaccuracy, preselection=PhotoScan.NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000)
    chunk.alignCameras()
    doc.save()
    
    ################################################################################################
    ### Build Dense Cloud ###
    ## Generate depth maps for the chunk.
    # buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering[, cameras], keep_depth=False, reuse_depth=False[, progress])
    # - Dense point cloud quality in [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
    # - Depth filtering mode in [AggressiveFiltering, ModerateFiltering, MildFiltering, NoFiltering]
    
    chunk.buildDepthMaps(quality = depthquality, filter = PhotoScan.MildFiltering)
    chunk.buildDenseCloud(point_colors = True)
    doc.save()
    
    ################################################################################################
    ### build mesh (optional) ###
    ## Generate model for the chunk frame.
    # buildModel(surface=Arbitrary, interpolation=EnabledInterpolation, face_count=MediumFaceCount[, source ][, classes][, progress])
    # - Surface type in [Arbitrary, HeightField]
    # - Interpolation mode in [EnabledInterpolation, DisabledInterpolation, Extrapolated]
    # - Face count in [HighFaceCount, MediumFaceCount, LowFaceCount]
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
#    chunk.buildModel(surface=PhotoScan.HeightField, interpolation=PhotoScan.EnabledInterpolation, face_count=PhotoScan.HighFaceCount)
#    chunk.buildModel(surface = PhotoScan.SurfaceType.HeightField, 
#                 interpolation=PhotoScan.Interpolation.EnabledInterpolation, 
#                 face_count=PhotoScan.FaceCount.HighFaceCount, 
#                 quality=PhotoScan.Quality.HighQuality, 
#                 vertex_colors=False) 
    
    ################################################################################################
    ### build texture (optional) ###
    ## Generate uv mapping for the model.
#    #buildUV(mapping=GenericMapping, count=1[, camera ][, progress])
#     - UV mapping mode in [GenericMapping, OrthophotoMapping, AdaptiveOrthophotoMapping, SphericalMapping, CameraMapping]
#    chunk.buildUV(mapping=PhotoScan.AdaptiveOrthophotoMapping)
#    # Generate texture for the chunk.
#     buildTexture(blending=MosaicBlending, color_correction=False, size=2048[, cameras][, progress])
#     - Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
#    chunk.buildTexture(blending=PhotoScan.MosaicBlending, color_correction=True, size=30000)
#    doc.save()
    
    ################################################################################################
    ### build DEM ###
    ## Build elevation model for the chunk.
    # buildDem(source=DenseCloudData, interpolation=EnabledInterpolation[, projection ][, region ][, classes][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    chunk.buildDem(source=PhotoScan.DenseCloudData, interpolation=PhotoScan.EnabledInterpolation, projection=chunk.crs)
    doc.save()
    
    ################################################################################################
    ## Build orthomosaic for the chunk.
    # buildOrthomosaic(surface=ElevationData, blending=MosaicBlending, color_correction=False[, projection ][, region ][, dx ][, dy ][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    # - Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
    chunk.buildOrthomosaic(surface=PhotoScan.DataSource.ElevationData, blending=PhotoScan.MosaicBlending, projection=chunk.crs)
    doc.save()
    chunk.exportOrthomosaic(save_ortho, image_format = PhotoScan.ImageFormatTIFF)#, format = PhotoScan.RasterFormat.RasterFormatTiles)
    
    ################################################################################################
    ## auto classify ground points (optional)
    #chunk.dense_cloud.classifyGroundPoints()
    #chunk.buildDem(source=PhotoScan.DenseCloudData, classes=[2])
    
    
    ################################################################################################
    # Create NDVI of the ortho
    # NDVI = (NIR - Red) / (NIR + Red)
    # Export Ortho - [RasterTransformNone, RasterTransformValue, RasterTransformPalette]
    if VI_flag == 1:
        try:
            chunk.raster_transform.formula = ["(B3/B2)*(B1/B2)"]
            chunk.raster_transform.calibrateRange()
            chunk.raster_transform.enabled = True
            save_NDVI = save_ortho.rpartition(".")[0] + "_NDVI.tif"
            chunk.exportOrthomosaic(save_NDVI, image_format = PhotoScan.ImageFormatTIFF, raster_transform=PhotoScan.RasterTransformNone)
        except:
            print("Could not save VI image.")
    else:
        pass
    
    print("Finished Processing" + save_file)
    doc.clear()
    return
    

#####-----------------------------------------------------------------------------------------------------------------------------------#######
def process_data(processday):    
    projname = processday.rpartition("Isolated/")[2].rpartition("/")[0].replace("/","-")
    saveproj = "C:/Users/thomasvanderweide/Documents/PhotoscanProjects/" + projname + ".psx"
    print(saveproj)

    save_orthoFold = processday + "orhto/"
    if not os.path.exists(save_orthoFold):
        os.mkdir(save_orthoFold)

    save_ortho = save_orthoFold + projname + ".tif"
    print(save_ortho)

    # NDVI from the mosaic?
    VI_flag = 1 # 0 - No, 1 - Yes
    quality = "Highest" # - Accuracy in [Highest, High, Medium, Low, Lowest]
    photoscanProcess(processday, saveproj, save_ortho, VI_flag, quality)



#####-----------------------------------------------------------------------------------------------------------------------------------#######
# Main Function
sys.stdout.write("Processing Started...")


field = ["C:/Users/thomasvanderweide/Documents/Isolated/Hartman/", 
      "C:/Users/thomasvanderweide/Documents/Isolated/Western/"]

for fn in field:
    for day in sorted(glob.iglob(fn + "*")):
        if fn.rpartition("Isolated/")[2].rpartition("/")[0] == "Hartman":
            fieldNum = ["2A", "2B"]
            for fieldID in fieldNum:
                dayfold = day.replace("\\","/")
                proj = fieldID
                processday = dayfold + "/" + proj + "/"
                onlyfiles = [f for f in os.listdir(processday)]
                if len(onlyfiles) > 2:
                    t0 = time.time()
                    process_data(processday)
                    tend = float(time.time() - t0)
                    sys.stdout.write("Script finished in " + "{:.2f}".format(tend) + " seconds.\n")
    
        elif fn.rpartition("Isolated/")[2].rpartition("/")[0] == "Western":
            fieldNum = ["1A", "1B"]
            for fieldID in fieldNum:
                dayfold = day.replace("\\","/")
                proj = fieldID
                processday = dayfold + "/" + proj + "/"
                onlyfiles = [f for f in os.listdir(processday)]
                if len(onlyfiles) > 2:
                    t0 = time.time()
                    process_data(processday)
                    tend = float(time.time() - t0)
                    sys.stdout.write("Script finished in " + "{:.2f}".format(tend) + " seconds.\n")


