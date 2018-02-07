# Python script which corrects images with bias and flat-field frames. 

#------Change the following parameters--------------------------------------------------------------------------------------#

# Input locations of images and name of target star. Note that bias frames and flat frames must be the same dimensions as science frames

star = "J06398+5157"
bias_loc = "/Users/rfb/Desktop/ART/Observation/2012-10-31/Bias/"
flat_loc = "/Users/rfb/Desktop/ART/Observation/2012-10-03/Flat_Frames/Sub_Frame/"
science_loc = "/Users/rfb/Desktop/ART/Observation/2012-11-03/J06398/"

# Input the wildcard indications of the images

bias = bias_loc + "B*.fit"
flat = flat_loc + "Flat-*.fit"
science = science_loc + "J*.fit"

#------Do not change the rest-----------------------------------------------------------------------------------------------#

# Define where master calibration frames are to be stored

bias_master_loc = bias_loc + "Bias_Master.fit"
flat_master_loc = flat_loc + "Flat_Master.fit"
flat_master_norm_loc = flat_loc + "Flat_Master_Norm.fit"

# Import iraf commands

from pyraf import iraf
import os

# Combine bias frames to create a master bias frame (stored in current working directory)

if os.path.exists(bias_master_loc):
    print ("Master bias frame already exists.")
else:
    print ("Creating master bias frame...")
    iraf.imcombine( bias, bias_master_loc, combine="median")
    print ("Master bias frame created.")

# Make a list of image filenames (with their path)

import glob

flat_list = glob.glob(flat)
science_list = glob.glob(science)

# Subtract the master bias frame from each of the flat field frames

print ("Subtracting master bias frame from flat field frames.")

for i in range(len(flat_list)):
    flat_field = flat_list[i]
    count = i + 1
    flat_field_cal = flat_loc + "Flat_cal_" + '{:03}'.format(count) + ".fit"
    if os.path.exists(flat_field_cal):
        print (flat_field_cal) + (" already exists.")
    else:
        iraf.imarith( flat_field, "-", bias_master_loc, flat_field_cal)

# Create a list of the calibrated flat field frames. Combine them to make a master flat field.
    
flat_cal = flat_loc + "Flat_cal*.fit"
if os.path.exists(flat_master_loc):
    print ("Master flat field frame already exists.")
else:
    print ("Creating master flat field frame...")
    iraf.imcombine( flat_cal, flat_master_loc, combine = "median")
    print ("Master flat field frame created.")

# Normalise the master flat field frame.
    
import pyfits
import scipy.stats

if os.path.exists(flat_master_norm_loc):
    print ("Normalised master flat field frame already exists.")
else:
    print ("Normalising master flat field frame...")
    flat_data = pyfits.getdata(flat_master_loc, 0)
    flat_mode_array = scipy.stats.mode(flat_data, axis=None)
    flat_mode = flat_mode_array[0][0]
    print ("Mode is ") + str(flat_mode)
    iraf.imarith( flat_master_loc, "/", flat_mode, flat_master_norm_loc)
    print ("Master flat field frame normalised.")
    new_flat_data = pyfits.getdata(flat_master_norm_loc, 0)
    new_flat_mode_array = scipy.stats.mode(new_flat_data, axis=None)
    new_flat_mode = new_flat_mode_array[0][0]
    print ("New mode is ") + str(new_flat_mode)
    
# Subtract the master bias from each of the science frames. Divide each science frame by the normalised master flat field.

print ("Subtracting the master bias from each of the science frames and then dividing each science frame by the normalised master flat field frame.")

if not os.path.exists(science_loc + "Less_bias/"):
    os.makedirs(science_loc + "Less_bias/")
    
if not os.path.exists(science_loc + "Cal/"):
    os.makedirs(science_loc + "Cal/")

for i in range(len(science_list)):
    science_frame = science_list[i]
    count = i + 1
    science_frame_minus_bias = science_loc + "Less_bias/" + star + "_less_bias_" + '{:04}'.format(count) +".fit"
    science_frame_cal = science_loc + "Cal/" + star + "_cal_" + '{:04}'.format(count) + ".fit"
    if os.path.exists(science_frame_minus_bias):
        print (science_frame_minus_bias) + (" already exists.")
    else:
        iraf.imarith( science_frame, "-", bias_master_loc, science_frame_minus_bias)
    if os.path.exists(science_frame_cal):
        print (science_frame_cal) + (" already exists")
    else:
        iraf.imarith( science_frame_minus_bias, "/", flat_master_norm_loc, science_frame_cal)


