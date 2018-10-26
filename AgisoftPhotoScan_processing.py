# Auto batch process for Agisoft Photoscan
# Starting code
# https://lastexiler.wordpress.com/2017/02/22/auto-batch-processing-code-for-photoscan/

# Run script in headless mode (without opening Agisoft) from command line
# photoscan.exe -r <script.py>
 
import PhotoScan
import os,re
 
## get the photo (.tif) list in specified folder
def getPhotoList(root_path, photoList):
    pattern = '.tif$'
    for root, dirs, files in os.walk(root_path):
        for name in files:
            if re.search(pattern,name):
                cur_path = os.path.join(root, name)
                #print (cur_path)
                photoList.append(cur_path)
 
    
## batch process
def photoscanProcess(root_path, save_file, save_ortho):
    #PhotoScan.app.messageBox('hello world! \n')
    PhotoScan.app.console.clear()
    
    ## construct the document class
    doc = PhotoScan.app.document
     
    ## save project
    psxfile = os.path.join(root_path, save_file)
    doc.save( psxfile )
    print ('&amp;gt;&amp;gt; Saved to: ' + psxfile)
    ## add a new chunk
#    chunk = doc.addChunk()
    
    ## Re-run in current document
    doc.open(psxfile)
    chunk = doc.chunk
    
    ## set coordinate system
    # - PhotoScan.CoordinateSystem("EPSG::4612") --&amp;gt; JGD2000
    chunk.crs = PhotoScan.CoordinateSystem("EPSG::4326") # WGS84
    
    ################################################################################################
#    ### get photo list ###
#    photoList = []
#    getPhotoList(root_path, photoList)
#    #print (photoList)
#    
#    ################################################################################################
#    ### add photos ###
#    # addPhotos(filenames[, progress])
#    # - filenames(list of string) – A list of file paths.
#    chunk.addPhotos(photoList)
#    
#    ################################################################################################
#    ### align photos ###
#    ## Perform image matching for the chunk frame.
#    # matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000[, progress])
#    # - Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy]
#    # - Image pair preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
#    chunk.matchPhotos(accuracy=PhotoScan.HighAccuracy, preselection=PhotoScan.ReferencePreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000)
#    chunk.alignCameras()
#    doc.save()
#    
#    ################################################################################################
#    ### build dense cloud ###
#    ## Generate depth maps for the chunk.
#    # buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering[, cameras], keep_depth=False, reuse_depth=False[, progress])
#    # - Dense point cloud quality in [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
#    # - Depth filtering mode in [AggressiveFiltering, ModerateFiltering, MildFiltering, NoFiltering]
#    chunk.buildDepthMaps(quality = PhotoScan.HighQuality, filter = PhotoScan.MildFiltering)
#    doc.save()
#    chunk.buildDenseCloud(point_colors = True)
#    doc.save()
#    
#    ################################################################################################
#    ### build mesh ###
#    ## Generate model for the chunk frame.
#    # buildModel(surface=Arbitrary, interpolation=EnabledInterpolation, face_count=MediumFaceCount[, source ][, classes][, progress])
#    # - Surface type in [Arbitrary, HeightField]
#    # - Interpolation mode in [EnabledInterpolation, DisabledInterpolation, Extrapolated]
#    # - Face count in [HighFaceCount, MediumFaceCount, LowFaceCount]
#    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
##    chunk.buildModel(surface=PhotoScan.HeightField, interpolation=PhotoScan.EnabledInterpolation, face_count=PhotoScan.HighFaceCount)
##    chunk.buildModel(surface = PhotoScan.SurfaceType.HeightField, 
##                 interpolation=PhotoScan.Interpolation.EnabledInterpolation, 
##                 face_count=PhotoScan.FaceCount.HighFaceCount, 
##                 quality=PhotoScan.Quality.HighQuality, 
##                 vertex_colors=False) 
#    
#    ################################################################################################
#    ### build texture (optional) ###
#    ## Generate uv mapping for the model.
#    # buildUV(mapping=GenericMapping, count=1[, camera ][, progress])
#    # - UV mapping mode in [GenericMapping, OrthophotoMapping, AdaptiveOrthophotoMapping, SphericalMapping, CameraMapping]
#    #chunk.buildUV(mapping=PhotoScan.AdaptiveOrthophotoMapping)
#    ## Generate texture for the chunk.
#    # buildTexture(blending=MosaicBlending, color_correction=False, size=2048[, cameras][, progress])
#    # - Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
#    #chunk.buildTexture(blending=PhotoScan.MosaicBlending, color_correction=True, size=30000)
#    
#    ################################################################################################
#    ## save the project before build the DEM and Ortho images
##    doc.save()
#    
#    ################################################################################################
#    ### build DEM (before build dem, you need to save the project into psx) ###
#    ## Build elevation model for the chunk.
#    # buildDem(source=DenseCloudData, interpolation=EnabledInterpolation[, projection ][, region ][, classes][, progress])
#    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
#    chunk.buildDem(source=PhotoScan.DenseCloudData, interpolation=PhotoScan.EnabledInterpolation, projection=chunk.crs)
#    doc.save()
    
    ################################################################################################
    ## Build orthomosaic for the chunk.
    # buildOrthomosaic(surface=ElevationData, blending=MosaicBlending, color_correction=False[, projection ][, region ][, dx ][, dy ][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    # - Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
#    chunk.buildOrthomosaic(surface=PhotoScan.ModelData, blending=PhotoScan.MosaicBlending, color_correction=True, projection=chunk.crs) # Uses mesh as the surface
#    chunk.buildOrthomosaic(surface=PhotoScan.DataSource.ElevationData, blending=PhotoScan.MosaicBlending, projection=chunk.crs)
    doc.save()
    chunk.exportOrthomosaic(save_ortho, image_format = PhotoScan.ImageFormatTIFF)
    
    ################################################################################################
    ## auto classify ground points (optional)
    #chunk.dense_cloud.classifyGroundPoints()
    #chunk.buildDem(source=PhotoScan.DenseCloudData, classes=[2])
    
    ################################################################################################

    
#########-------------------------------- main ------------------------------------------------------------------------------##############
folder = "H:/Terroir/Bitner/photo/Processed_1/vigCorrected/"
saveproj = "Bitner.psx"
saveortho = "H:/Terroir/Bitner/photo/Processed_1/vigCorrected/BitnerOrtho.tif"
photoscanProcess(folder, saveproj, saveortho)


