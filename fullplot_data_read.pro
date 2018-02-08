;Colm Keyes
;Reading .npz file into IDL interpreter.
;17/10/17

;#########################################################################################
;Loading time dependent flux data
 
Template1= Ascii_template('/Users/guest01/Desktop/Colm_keyes/Colm_full_flux.txt')
Template2= Ascii_template('/Users/guest01/Desktop/Colm_keyes/Colm_time.txt')

data_read1=read_ascii('/Users/guest01/Desktop/Colm_keyes/Colm_full_flux.txt')
data_read2=read_ascii('/Users/guest01/Desktop/Colm_keyes/Colm_time.txt')

time=data_read2.field1
full_flux=data_read1.field1

;##########################################################################################

std=stddev(full_flux)
m=mean(full_flux)
a=0

;##########################################################################################
;Removing bad data points which are outside 3 sigma stddev
foreach i , full_flux do begin
 if a+1 eq N_elements(time) then break
    if abs(i-m) gt 3*std then begin
      print, abs(i-m)
      remove, [a], full_flux, time
    endif
    if i eq 0 then begin
      remove, [a], full_flux, time
    endif
  a=a+1
endforeach

b=0
foreach k , time do begin
  if b+1 eq N_elements(time) then break
  if time[b] - time[b+1] gt 0 then begin
    print,"this is a bad point"+string(b)
    remove, [b], full_flux, time
  endif
  if time[b] lt 0 then begin
    remove , [b], full_flux, time
  endif
  if full_flux[b] lt 0.2 then begin
    remove, [b], full_flux, time
  endif
  
  b=b+1
endforeach


;#########################################################################################
; Generating the Fourier transform of the time-series data set

CL_fpar, time, fpar
dfourt, time, full_flux, fpar,freq,b,c

;#########################################################################################
;Plotting the power specturm of the data set

!p.multi = [0,1,3,0,0]
plot, freq, sqrt(c^4), xrange=[0,4000], xtitle='Frequency/day', ytitle='Amplitude', title='Power Spectrum for 2013-01-12'
cols=getcolor(/load)
plot, freq, sqrt(c^4), xrange=[0,500], xtitle='Frequency/day', ytitle='Power', title='Power Spectrum for 2013-01-12'

end
