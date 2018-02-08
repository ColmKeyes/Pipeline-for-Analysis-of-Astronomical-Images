;Colm Keyes
;10/10/17
;Fourier transform for inputted light curve data
;######################################################################################################
;######################################################################################################
;reading in data from the .dat files


Template1= Ascii_template('/Users/guest01/Desktop/art_data/2017-11-16/Cal/Output_Images/time_flux.dat')
data_read= read_ascii('/Users/guest01/Desktop/art_data/2017-11-16/Cal/Output_Images/time_flux.dat', TEMPLATE=Template1)
 

time_array=Double(data_read.Field1)
flux_array=reform(data_read.Field2)
time_array_rel= time_array[*] - time_array[0]

;######################################################################################################
;This is a check to see which indices of time_array_rel are in the wrong position 

std=stddev(flux_array)
m=mean(flux_array)

a=0
b=0
foreach k , time_array_rel do begin
  if b+1 eq N_elements(time_array_rel) then break
  if time_array_rel[b] - time_array_rel[b+1] gt 0 then begin
    remove, [b], flux_array, time_array_rel
    print,"this is a bad point"+string(b)
  endif
  
  b=b+1
endforeach

;######################################################################################################
; Generating the Fourier transform of the time-series data set

CL_fpar, time_array_rel, fpar
dfourt, time_array_rel, flux_array, fpar,freq,b,c


;######################################################################################################
;Plotting the power specturm of the data set

cols=getcolor(/load)
plot, freq, sqrt(sqrt(c^4))
cd, '~/Desktop/Colm_Keyes/IDL_codes/'
set_plot, 'PS'
device,file='2013-01-12.ps',/encapsulated,/color,xsize=20,ysize=20

end


