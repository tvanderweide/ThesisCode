# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 14:43:36 2018

Read in Near-Surface Camera Images
Vignette corrected Images
Get out VI overtime chart
v2
Plot Pyranometer data on same chart

8/9/2018
@author: thomasvanderweide
"""

import os
import glob
import numpy as np
from skimage import io
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, date
import pickle
import pandas as pd

#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def readPyr(fn, fieldname):
    # Read the Pyr data
    Pyranometer = []
    pyrDate = []
    list_of_dates = []
    count = 0
    for pyr in sorted(glob.iglob(fn + '/Pyranometer/*_pyr.pkl')):
        pyr = pyr.rpartition('\\')[2]
        hour = pyr.rpartition("_")[0].rpartition("_")[0].rpartition("_")[2]
        hour = hour [:2]
        day = pyr.rpartition("_")[0].rpartition("_")[0].rpartition("_")[0].rpartition("_")[2]
        pyrDate = date(2018, int(day[:2]), int(day[2:]))
        pyr = os.path.join(fn + "/Pyranometer/" + pyr)
#        print(pyr)
        
        if int(hour) == 12:
            list_of_dates.append(matplotlib.dates.date2num(pyrDate))
            with open(pyr, 'rb') as f:
                data = pickle.load(f)
            temp_pyr = []
            for entry in data[3]:
                # If there was a failure in data collection, print the day it happened
                if (round(float(entry)) == -9999):
                    print(pyr)
                    print(entry)
                temp_pyr.append(entry)
    
            Pyranometer.append(np.average(temp_pyr))
            count += 1

    plt.figure()
    plt.plot_date(list_of_dates, Pyranometer, fmt="-o")
    plt.title('Pyranometer Data for %s' %fieldname)
    plt.show
    return Pyranometer, list_of_dates


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def convert_VI(fn2, field):
  
#    hours = ["10","11","12","13","14"]
#    for hour in hours:
    hour = "12"
    # Read in the TIF files
    infile = fn2 + "/2018_*_" + hour + "*.tif"
    arr = []
    dates = []
    for img in sorted(glob.iglob(infile)):
        # Extract the dates from the JPG filename
        d1 = img.rpartition("\\")[2]
        d2 = d1.rpartition("_" + hour)[0]
        dates.append(d2)
        
        # Read in the images
        im = io.imread(img)
        # Load the bands
        R, G, B = 0, 1, 2
        NIR = im[:,:,R]
        Green = im[:,:,G]
        Blue = im[:,:,B]
        
        # Convert into FVI Value
        FVI = (Blue / Green) * (NIR / Green)
#        CVI = (NIR/Green) * (Red/Green)
        
        # Get the mean FVi Value
        FVIval = np.ma.masked_invalid(FVI).mean()
        
        arr.append(FVIval)

    dtime = date_process(dates)
            
    return arr, dtime


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def date_process(dates):
    dtime = []
    for d in dates:
        dformat = d.rpartition("_")[0] + " " + d.rpartition("_")[2][:2] + " " + d.rpartition("_")[2][2:]
#        print(dformat)
        date = datetime.strptime(dformat, '%Y %m %d')
        dtime.append(date)
    return dtime


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def plot_fun(FVI_arr, dtimes, Field, save_file):
    fig = plt.figure(figsize=(15,9))
    ax = fig.add_subplot(111)
    
    # Set the tick labels font
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontname('Arial')
        label.set_fontsize(20)
    
    title_font = {'fontname':'Arial', 'size':'34', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'} # Bottom vertical alignment for more space
    axis_font = {'fontname':'Arial', 'size':'26', 'color':'black'}
  
    ax.plot_date(x = dtimes, y = FVI_arr, fmt="-o")

#    minpyr = min(Pyranometer)
#    maxpyr = max(Pyranometer)
#    normPyr = ((Pyranometer - minpyr) / (maxpyr - minpyr))
#    ax.plot_date(list_of_PyrDates, normPyr, fmt="-o")
    
    ax.set_xlabel("Dates", **axis_font)
    ax.set_ylabel("FVI", **axis_font)
    ax.set_title(Field + " mean FVI values", **title_font)
    ax.grid(True)
#    fig.show()
    fig.savefig(save_file, bbox_inches='tight', dpi = 450)
    return


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def plot_pyr(Pyranometer, list_of_PyrDates, Field, save_pyr):
    fig = plt.figure(figsize=(15,9))
    ax = fig.add_subplot(111)
    
    # Set the tick labels font
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontname('Arial')
        label.set_fontsize(20)
    
    title_font = {'fontname':'Arial', 'size':'34', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'} # Bottom vertical alignment for more space
    axis_font = {'fontname':'Arial', 'size':'26', 'color':'black'}
  
    ax.plot_date(x = list_of_PyrDates, y = Pyranometer, fmt="-o")

#    minpyr = min(Pyranometer)
#    maxpyr = max(Pyranometer)
#    normPyr = ((Pyranometer - minpyr) / (maxpyr - minpyr))
#    ax.plot_date(list_of_PyrDates, normPyr, fmt="-o")
    
    ax.set_xlabel("Dates", **axis_font)
    ax.set_ylabel("W mˉ²", **axis_font)
    ax.set_title(Field + " Pyranometer values", **title_font)
    ax.grid(True)
#    fig.show()
    fig.savefig(save_pyr, bbox_inches='tight', dpi = 450)
    return


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def plot_fieldsVI(df, outfile):
#    color=iter(plt.cm.rainbow(np.linspace(0,1,4)))
    color=iter(plt.cm.jet([0.2,0.25,0.70,0.75]))
    
    # Break the array up by Location
    df['DateTime'] = pd.to_datetime(df['Dates'])
    df.set_index('DateTime', inplace=True)
    fig, ax = plt.subplots(figsize=(18,10))
    for Loc_key, grp in df.groupby(['Field']):
        c=next(color)
        grp.plot(x=grp.index, y= 'FVI', style='-o', ax=ax, color = c)
        
    
    ax.legend(['Western_1A', 'Western_1B', 'Hartman_2A', 'Hartman_2B'])
    plt.title("All Fields Field Imagery FVI")
    # Save the figure at high resolution
    fig.savefig(outfile, format='png', bbox_inches='tight', dpi=600)
    return


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
#Run the program
print("Stating to plot the Field image VI values over time...")

# Define what files to rename
main_folder = "N:/Data02/projects-active/IGEM_Kairosys/2018 Data/Fieldsv3/"

FieldList = ['Field1A', 'Field1B', 'Field2A', 'Field2B']
FieldPyr = ["1B","2B"]
i = 0
for field in FieldList:
    fieldNum = field[-2:]
    fn1 = os.path.join(main_folder, field)
    print(fn1)
    fn2 = os.path.join(fn1, "Processed_2")
    fn3 = os.path.join(fn2, "vigCorrected")
    fn4 = os.path.join(fn3, "Calibrated_3")
    fn4 = fn4.replace("\\","/")
    print("Processing: " + field)
    
#    if fieldNum in FieldPyr:
#        Pyranometer, list_of_PyrDates = readPyr(fn1, field)
#        out_pyr = main_folder + field + "_pyr.png"
#        plot_pyr(Pyranometer, list_of_PyrDates, field, out_pyr)
        
    FVI_arr, dtimes = convert_VI(fn3, field)
#    outfile = main_folder + field + "_FVI.png"
#    plot_fun(FVI_arr, dtimes, field, outfile)
    dataset = pd.DataFrame({'Dates':dtimes, 'FVI': FVI_arr})
    dataset['Field'] = pd.Series(field, index=dataset.index)
    if i == 0:
        CombinedDF = dataset.copy()
    else:
        CombinedDF = CombinedDF.append(dataset)

    i = i + 1



outfile = main_folder + "Fields_FVI.png"
plot_fieldsVI(CombinedDF, outfile)


