# Python script which extracts the wanted photometric data from the s-extractor output catalogues. It then plots this data and returns a .npz file and a .dat file which contain the time and flux ratio arrays.

#------Change the following parameters--------------------------------------------------------------------------------------#

# Define locations in which image files and photometric data are stored.

catalogue_loc = "/Users/rfb/Desktop/ART/Observation/2012-10-26/Data_reduction/Phot_Catalogues/"
image_loc = "/Users/rfb/Desktop/ART/Observation/2012-10-26/Data_reduction/"

# Define where output is to be stored.

output_loc = "/Users/rfb/Desktop/ART/Observation/2012-10-26/Output/"

# Specify number of output parameters that s-extractor returned (number of header lines).

output_param_num = 17

# Specify the columns in the s-extractor catalogues which contain the x, y and flux values that you want to use.

x_column = 13
y_column = 14
flux_column = 1

# Define wild card specifications of the files.

catalogue = catalogue_loc + "*_phot_*.cat"
image = image_loc + "*_cal_*.fit"

# Set positions of target and reference stars

target_pos = [467., 215.]
ref1_pos = [220., 338.]
ref2_pos = [286., 242.]

# Set portion of lightcurve that you want to be zoomed in on. You may want to inspect the output images before deciding this.

# Raw flux plot (J06398+5157.png).
x1, x2, y1, y2 = 0.0, 0.03, 30000., 60000.

# Flux ratio plot (J06398+5157_Ratio.png).
x3, x4, y3, y4 = 0.0, 0.03, 0.8, 1.2

# Define thresholds for target and reference stars

target_thresh = 20000.
ref_thresh = 10000.

#------Do not change the rest-----------------------------------------------------------------------------------------------#

# Check if the output directory exists. If it does, check if it's ok to overwrite the output files (exit if no, continue if yes). If it doesn't, create it.

import os

if os.path.exists(output_loc):
    a = raw_input("Output directory exists. Is it ok to overwrite the files in the output directory? (y/n)\n")
    if a == 'n' or a == 'no' or a == 'No':
        import sys
        sys.exit()
else:
    os.makedirs(output_loc)
    
# Import necessary libraries.

import glob
import pyfits
import numpy
import math

# Define list of paths to filenames.

catalogue_list = glob.glob(catalogue)
image_list = glob.glob(image)

# Make a list of the inputted position for the target and reference stars
  
ref_list = [target_pos, ref1_pos, ref2_pos]

# Define empty list to store times at which images were taken and an empty array to store Julian date values.

universal_time = []
jd_time = numpy.zeros(shape=(len(image_list)))
 
# For loop to make time arrays.

for i in range(len(image_list)):
    
    image = image_list[i]
    image_time = pyfits.getval(image, "date-obs", 0)
    universal_time.append(image_time)
    image_jtime = pyfits.getval(image, "jd", 0)
    jd_time[i] = image_jtime

# Subtract initial time from  time array.
   
jd_time_base = jd_time - jd_time[0]

# Define empty arrays to store photometric values.

flux_target = numpy.zeros(len(catalogue_list))
flux_reference = numpy.zeros(len(catalogue_list))
flux_references = numpy.zeros(shape = (len(ref_list) - 1, len(catalogue_list)))

# For loop to extract photometric values from ascii catalogues.

for i in range(len(catalogue_list)):
      
    cat = catalogue_list[i]
    data_file = open(cat, 'r')
      
    # Ignore the header lines
    for header_line in range(output_param_num):
        header = data_file.readline()
          
    # Define empty arrays to store the parameters for each catalogue
    flux_objs = numpy.zeros(shape=100)

    # Set a counter variable
    count = 0

    # Set indicators to show is the star has been found. These will stay at -1 if the star is not found.
    target = -1
    ref_line = numpy.zeros(len(ref_list) - 1) - 1.
    
    # Loop over the lines in the catalogue and extract the columns of interest
    for line in data_file:
          
        # Remove /n from the end of each line
        line = line.strip()
          
        # Divide the line up into columns
        columns = line.split()

        # Specify columns of interest
        flux = float(columns[flux_column])
        x_val = float(columns[x_column])
        y_val = float(columns[y_column])

        # Find distance from object to specified target position
        radius = math.sqrt((ref_list[0][0] - x_val)**2 + (ref_list[0][1] - y_val)**2)

        # If this distance is less than 10 pixels and the object flux is over the target star threshold, this object is defined as the target star.
        if radius < 10. and flux > target_thresh:
            target = count
            print 'x = ' + str(x_val), 'y = ' + str(y_val), 'Line: ' + str(target)

        # Do the same for the reference stars. These must have a flux over the reference star threshold.
        for j in range(len(ref_list) - 1):
            ref_star = ref_list[j + 1]
            ref_radius =  math.sqrt((ref_star[0] - x_val)**2 + (ref_star[1] - y_val)**2)
            if ref_radius < 10. and flux > ref_thresh:
                ref_line[j] = count

        # Fill up flux array (contains the flux for each object in this catalogue).
        flux_objs[count] = flux

        # Increase counter.
        count = count + 1
          
    # Insert the values into the arrays. If no star corresponding to the given position was found, a zero is inserted.
    if target >= 0:
        flux_target[i] = flux_objs[target]
    else:
        flux_target[i] = 0
        
    for k in range(len(ref_list) - 1):
        if ref_line[k] >= 0:
            flux_references[k, i] = flux_objs[ref_line[k]]
        else:
            flux_references[k, i] = 0

    # Find the sum of the references star fluxes and insert this into an array.
    flux_reference[i] = numpy.sum(flux_references[:, i])
    data_file.close()

# Calculate the flux ratio.
    
flux_ratio = flux_target / flux_reference

# Replace NaNs in the flux_ratio array with zeros.

for i in range(len(flux_ratio)):
    num = flux_ratio[i]
    if math.isnan(num):
        flux_ratio[i] = 0

# Find linear fit to the data. Normalise flux_ratio by dividing by the linear fit.

linfit = numpy.polyfit(jd_time, flux_ratio, 1)
fit = numpy.poly1d(linfit)
norm_flux_ratio = flux_ratio / fit(jd_time)

# Save the time and flux ratio arrays.

textfile = open(output_loc + 'time_flux.dat', 'w')
for i in range(len(jd_time)):
    print >> textfile, str(jd_time[i]).rjust(15), str(norm_flux_ratio[i]).rjust(20)
textfile.close()
numpy.savez(output_loc + 'flux_ratio_save', jd_time, norm_flux_ratio)

# Calculate and save the reference star flux ratios.
for i in range(len(ref_list)-1):
    reference_ratio = flux_references[i] / flux_reference
    reffile = open(output_loc + 'ref_flux_' + str(i+1) + '.dat', 'w')
    for j in range(len(jd_time)):
        print >> reffile, str(jd_time[j]).rjust(15), str(reference_ratio[j]).rjust(20)
    reffile.close()
    numpy.savez(output_loc + 'ref_ratio_save' + str(i+1), jd_time, reference_ratio)

# Plot the results

import matplotlib.pyplot as plt

# Absolute photometry plots: plot the full night of raw flux data and a zoomed in portion.

plt.figure()

plt.subplot(211)
plt.plot(jd_time_base, flux_target, 'ro', markersize = 2)
plt.ylabel('Flux (counts)', fontsize=10)
plt.title('J06398+5157 Flux')
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)

plt.subplot(212)
plt.plot(jd_time_base, flux_target, 'ro', markersize = 2)
plt.axis([x1, x2, y1, y2])
plt.xlabel('Time (decimal days)', fontsize=10)
plt.ylabel('Flux (counts)', fontsize=10)
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)
plt.savefig(output_loc + 'J06398+5157_Flux')

# Relative photometry: plot the full night of flux ratio data and a zoomed in portion. 

plt.figure()
plt.subplot(211)
plt.plot(jd_time_base, norm_flux_ratio, 'go', markersize = 2)
plt.ylabel('Flux Ratio', fontsize=10)
plt.title('J06398+5157 Flux Ratio (using sum of two reference stars)')
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)

plt.subplot(212)
plt.plot(jd_time_base, norm_flux_ratio, 'go', markersize = 2)
plt.axis([x3, x4, y3, y4])
plt.xlabel('Time (decimal days)', fontsize=10)
plt.ylabel('Flux Ratio', fontsize=10)
plt.xticks(fontsize=7)
plt.yticks(fontsize=7)
plt.savefig(output_loc + 'J06398+5157_Ratio')    
