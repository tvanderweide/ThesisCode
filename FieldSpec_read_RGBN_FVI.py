# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 10:54:33 2018
Read FieldSpec Data and display
v3
Display as NGB and save FVI plots
@author: thomasvanderweide
"""
from specdal import reader as r
import pandas as pd
import csv
import numpy as np
import glob
import os
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from numpy import linspace

#import matplotlib.pyplot as plt
from matplotlib.dates import date2num , DateFormatter
import datetime as dt


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def get_outfile(ASD_filepath, Field):
    # ASD_filepath = "N:/Data02/projects-active/IGEM_Kairosys/Spectral_Projects_TVDW/ASDfiles/GHSmallASD/Data/0730/0730G00013.asd.ref"
    asd_file1 = ASD_filepath.rpartition("\\")[0]    # File path except the /file_name.asd.ref
    asd_file2 = asd_file1.rpartition("\\")[0]       # File path except the date
    outfile1 = asd_file2 + '/csv/'
    print(outfile1)
    if not os.path.exists(outfile1):
        os.makedirs(outfile1)
    outfile2 = outfile1 + Field +'.csv'
    return outfile2


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def write_to_csv(ASD_avg, outfile):
    with open(outfile, 'a') as csvfile:
        outwriter = csv.writer(csvfile, delimiter= ',', lineterminator = '\n')
        # Write the spectra data
        outwriter.writerow(ASD_avg)


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def create_Field_Num_arr():
    Field1_names = []
    for n in range(0,10):
        nz = str(n).zfill(5)
        Field1_names.append(nz)
        
    Field2_names = []
    for n in range(10,20):
        nz = str(n).zfill(5)
        Field2_names.append(nz)
        
    Field3_names = []
    for n in range(20,30):
        nz = str(n).zfill(5)
        Field3_names.append(nz)
    
    Field4_names = []
    for n in range(30,40):
        nz = str(n).zfill(5)
        Field4_names.append(nz)
        
    Field5_names = []
    for n in range(40,50):
        nz = str(n).zfill(5)
        Field5_names.append(nz)
        
    Field6_names = []
    for n in range(50,60):
        nz = str(n).zfill(5)
        Field6_names.append(nz)
    
    Field7_names = []
    for n in range(60,70):
        nz = str(n).zfill(5)
        Field7_names.append(nz)
        
    Field8_names = []
    for n in range(70,80):
        nz = str(n).zfill(5)
        Field8_names.append(nz)
        
    Field9_names = []
    for n in range(80,90):
        nz = str(n).zfill(5)
        Field9_names.append(nz)
        
    Field10_names = []
    for n in range(90,100):
        nz = str(n).zfill(5)
        Field10_names.append(nz)

    Field11_names = []
    for n in range(100,110):
        nz = str(n).zfill(5)
        Field11_names.append(nz)
        
    return Field1_names, Field2_names, Field3_names, Field4_names, Field5_names, Field6_names, Field7_names, Field8_names, Field9_names, Field10_names, Field11_names



#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def format_insert(c1, c2, asd_row):
    asd_row.insert(0, c2)
    asd_row.insert(0, c1)
    return asd_row


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def iter_folders(input_folder, Field):
    # Create number arrays for each imaging area
    p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11 = create_Field_Num_arr()
    
    Locations = {
            'Point-1': p1, 
            'Point-2': p2, 
            'Point-3': p3, 
            'Point-4': p4, 
            'Point-5': p5, 
            'Point-6': p6, 
            'Point-7': p7, 
            'Point-8': p8, 
            'Point-9': p9, 
            'Point-10': p10, 
            'Point-11': p11
            }

    # Iterate through the days
    i = 0
#    for day in sorted(glob.iglob(input_folder + "*")):
    for day in sorted(glob.iglob(input_folder + "*")):
        asd_date = day.rpartition("\\")[2]          # ex) "6-12-2018"
        print(asd_date)
        if asd_date not in ["ASD_Files", "csv"]:
#        if asd_date == "6-12-2018":    
            print(day)
            df_arr = []
            for refasd in sorted(glob.iglob(day + "/ref/*.ref")):
#                print(refasd)
                # Create the header
                if i == 0:
                    outfile = get_outfile(refasd, Field)
                    ASD = r.read_asd(refasd)
                    start = int(ASD[1]['wavelength_range'][0])
                    stop = int(ASD[1]['wavelength_range'][1])
                    N = stop - start + 1
                    xnp = np.linspace(start,stop,N,dtype=int) # Wavelength header
                    x = xnp.tolist()
                    labels = format_insert('Location','Date', x)
                    mean_df = pd.DataFrame(columns=labels)
#                    write_to_csv(labels, outfile)
                    i += 1

                # Extract the ASD from the correct Field
                asd_name = refasd.rpartition("\\")[2]       # Western_1B_6-12_00109.asd.ref
                asd_field1 = asd_name.rpartition("_")[0]    # Western_1B_6-12
                asd_field = asd_field1.rpartition("_")[0]   # Western_1B
                if asd_field == Field:
                    # Get the asd Number
                    asd_num = asd_name.rpartition(".")[0]       # ex) 'Western_1B_6-12_00109.asd'
                    asd_num2 = asd_num.rpartition(".")[0]       # ex) 'Western_1B_6-12_00109'
                    asd_num3 = asd_num2.rpartition("_")[2]      # ex) '00109'
#                    print(asd_num3)
                    
                    for Loc, num_list in Locations.items():
                        for num in num_list:
                            if num == asd_num3:
#                                print(Loc)
                                # Read in the file into PD Series
                                ASD = r.read_asd(refasd)
#                                print(ASD)
                                # extract the relevant reflectance values
                                x_vals = ASD[0]['tgt_reflect']
#                                # Gets the reflectance values into an array
                                dx = x_vals.get_values()
                                row = []
                                row.insert(0, Loc)
                                row.insert(1, asd_date)
                                for x in dx:
                                    row.append(x)
#                                print(row)
                                df_arr.append(row)

            # Create a dataframe with all of the entries from the field selected            
            day_df = pd.DataFrame.from_records(df_arr, columns=labels)
            # Group these entries by Location and average the spectra for each "point"
            mean_day_df = day_df.groupby(['Location', 'Date'], sort=False).mean().reset_index()
            frames = [mean_df, mean_day_df]
            mean_df = pd.concat(frames)
            
#    mean_df.to_csv(outfile)
    return mean_df, outfile, Field


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def plot_fun(df, outfile, Field):
    # Break the array up by Location
    for Loc_key, grp in df.groupby(['Location']):
        # Define the color map for each grp
        cm_subsection = linspace(0.0, 1.0, grp.shape[0] + 1) 
        colors = [ cm.summer(x) for x in cm_subsection ]
        fig, ax = plt.subplots()
        i = 1
        mylabels = []
        # Break each location up by Dates, plot each date as a line on the graph
        for dat_key, grp_two in grp.groupby(['Date']):
            mylabels.append(dat_key)
            grp_three = grp_two.drop('Date', axis=1)
            grp_three = grp_three.transpose()
            grp_three.columns = grp_three.iloc[0]
            grp_four = grp_three.iloc[1:]
            ax = grp_four.plot(kind='scatter', c=colors[i], ax=ax)
            i += 1
#        ax.set_ylim(0, 1)
        plt.legend(labels = mylabels[::-1], loc='upper left')
        plt.title(Field + " " + Loc_key)
        plt.show()
        
        # Save the figure at high resolution
#        fig.savefig(outfile[:-4] + "_" + Loc_key + '_FVI.png', format='png', dpi=1200)
    return
    

#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def plot_VI(df, outfile, Field):
    # Break the array up by Location
    for Loc_key, grp in df.groupby(['Location']): 
        pd.to_datetime(grp['Date'])
        grp.set_index('Date', inplace=True)
        fig, ax = plt.subplots(figsize=(18,10))
        grp.plot(x=grp.index, y= 'FVI', style='-o', ax=ax)
        plt.legend(loc='upper left')
        plt.title(Field + " " + Loc_key + " FVI")
        plt.show()
        
        # Save the figure at high resolution
        fig.savefig(outfile[:-4] + "_" + Loc_key + '_FVI.png', format='png', dpi=1200)
    return


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def plot_fieldsVI(df, outfile, Field):
#    color=iter(plt.cm.rainbow(np.linspace(0,1,4)))
    color=iter(plt.cm.jet([0.2,0.25,0.70,0.75]))
    
    # Break the array up by Location
    df['DateTime'] = pd.to_datetime(df['Date'])
    df.set_index('DateTime', inplace=True)
    fig, ax = plt.subplots(figsize=(18,10))
    for Loc_key, grp in df.groupby(['Location']):
        c=next(color)
        grp.plot(x=grp.index, y= 'FVI', style='-o', ax=ax, color = c)
        
    
    ax.legend(['Western_1A', 'Western_1B', 'Hartman_2A', 'Hartman_2B'])
    plt.title(Field + " FVI")
    # Save the figure at high resolution
    fig.savefig(outfile, format='png', bbox_inches='tight', dpi=600)
    return


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
def formatRGB(df):
    # Define the wavelength ranges for each color
    # Create a column of Blue, Green, Red, NIR
#    Blue: 475 +- 20nm
#    Green: 550 +- 20nm
#    Red: 660 +- 20nm
#    NIR: 850 +- 30 nm
    Blue_head = list(range(455,495))
    Green_head = list(range(530,570))
    Red_head = list(range(640,680))
    NIR_head = list(range(820,880))
    
    df['Blue'] = df[Blue_head].mean(axis=1)
    df['Green'] = df[Green_head].mean(axis=1)
    df['Red'] = df[Red_head].mean(axis=1)
    df['NIR'] = df[NIR_head].mean(axis=1)
    
    Blue = df['Blue']
    Green = df['Green']
    NIR = df['NIR']
    
    df['FVI'] = (Blue/Green) * (NIR/Green)
    FVI_df = df[['Location','Date','FVI']]
    return FVI_df


#####-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#####
#Run the program
print("Stating to work with the FieldSpec Files...")

# Define what files to rename
fn = 'N:/Data02/projects-active/IGEM_Kairosys/2018 Data/HyperspectralScans/'
Field_ID = [0,1,2,3]  # 0 = Western_1A, 1 = Western_1B, 2 = Hartman_2A, 3 = Hartman_2B
Field_names = ['Western_1A', 'Western_1B', 'Hartman_2A', 'Hartman_2B']

for Field_num in Field_ID:
    Field = Field_names[Field_num]
    print("Processing: " + Field)
    # Process the ASD Files
    mean_df, outfile, Field = iter_folders(fn, Field)
    # Create a df with only RGB values
    FVI_df = formatRGB(mean_df)
    groups = FVI_df.groupby(['Location'])
    PointDF = groups.get_group("Point-10")
    PointDF['Location'] = PointDF['Location'].replace("Point-10", Field + " Point-10")
    if Field_num == 0:
        CombinedDF = PointDF.copy()
    else:
        CombinedDF = CombinedDF.append(PointDF)

outfile = fn + "csv/Images/FVI/Fields_Point-10_FVI.png"
#plot_fieldsVI(CombinedDF, outfile, "All_Fields")
# Plot the VI values over time
#plot_VI(FVI_df, outfile, Field)
