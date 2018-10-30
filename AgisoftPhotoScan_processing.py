'''
Auto batch process for Agisoft Photoscan
 Processes all tif images into a cropped orthomosaic
 Needs a shp and shx file in the same folder as the images to crop the orthomosaic
 

Run script in headless mode (without opening Agisoft) from command line
 photoscan.exe -r <script.py>

References
 https://lastexiler.wordpress.com/2017/02/22/auto-batch-processing-code-for-photoscan/
 https://mapbox.s3.amazonaws.com/playground/perrygeo/rasterio-docs/cookbook.html
'''
import PhotoScan
import os, re, time


#####-----------------------------------------------------------------------------------------------------------------------------------#######
def crop_ortho(sf, fn):
    try:
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
    
    except:
         print("This computer is missing something needed to crop the orthomosaic.")

    return


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
def photoscanProcess(root_path, save_file, save_ortho, NDVI_flag, CropOrtho_flag, sf):
    # Clear the Console
    PhotoScan.app.console.clear()
    
    # Enable GPU Processing
    PhotoScan.app.gpu_mask = 2 ** len(PhotoScan.app.enumGPUDevices()) - 1 #setting GPU mask
    if PhotoScan.app.gpu_mask:
        PhotoScan.app.cpu_enable = False  
    else:
        PhotoScan.app.cpu_enable = True
    
    ## construct the document class
    doc = PhotoScan.app.document
    
    ## save project
    psxfile = os.path.join(root_path, save_file)
    doc.save( psxfile )
    print ('&amp;gt;&amp;gt; Saved to: ' + psxfile)
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
    getPhotoList(root_path, photoList)
    # Add photos to list
    chunk.addPhotos(photoList)
    
    ################################################################################################
    ### Align Photos ###
    ## Perform image matching for the chunk frame.
    # matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000[, progress])
    # - Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy]
    # - Reference Preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
    
    chunk.matchPhotos(accuracy=PhotoScan.MediumAccuracy, preselection=PhotoScan.NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000)
    chunk.alignCameras()
    doc.save()
    
    ################################################################################################
    ### Build Dense Cloud ###
    ## Generate depth maps for the chunk.
    # buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering[, cameras], keep_depth=False, reuse_depth=False[, progress])
    # - Dense point cloud quality in [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
    # - Depth filtering mode in [AggressiveFiltering, ModerateFiltering, MildFiltering, NoFiltering]
    
    chunk.buildDepthMaps(quality = PhotoScan.MediumQuality, filter = PhotoScan.MildFiltering)
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
    if NDVI_flag == 1:
        chunk.raster_transform.formula = ["(B3-B1)/(B3+B1)"]
        chunk.raster_transform.calibrateRange()
        chunk.raster_transform.enabled = True
        save_NDVI = save_ortho.rpartition(".")[0] + "_NDVI.tif"
        chunk.exportOrthomosaic(save_NDVI, image_format = PhotoScan.ImageFormatTIFF, raster_transform=PhotoScan.RasterTransformNone)
    else:
        pass
    
    
    ################################################################################################
    # Crop the orthomosaic to the region of interest
    if CropOrtho_flag == 1:
        crop_ortho(sf, save_ortho)
        if NDVI_flag == 1:
            crop_ortho(sf, save_NDVI)
    else:
        pass
    
    print("Finished Processing" + save_file)
    doc.clear()
    return
    

#####-----------------------------------------------------------------------------------------------------------------------------------#######
# Main Function
print("Script Started...")
t0 = time.time()

folder = "H:/Terroir/Bitner/photo/Processed_1/vigCorrected/"
saveproj = "Bitner1.psx"
save_ortho = "H:/Terroir/Bitner/photo/Processed_1/vigCorrected/BitnerOrtho1.tif"

# NDVI from the mosaic?
NDVI_flag = 1 # 0 - No, 1 - Yes

# Crop the orthomosaic?
CropOrtho_flag = 1 # 0 - No, 1 - Yes
# Shape file location (Needed for cropping the ortho, just make whatever if CropOrtho = 0)
sf = "H:/Terroir/Bitner/Bitner.shp"

photoscanProcess(folder, saveproj, save_ortho, NDVI_flag, CropOrtho_flag, sf)

tend = float(time.time() - t0)

print("Script finished in " + "{:.2f}".format(tend) + " seconds.\n")
    


