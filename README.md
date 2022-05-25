# FoamPi

Adiabatic temperature rise (ATR) is an important method for determining isocyanate conversion in polyurethane foam reactions as well as many other exothermic chemical
reactions. ATR can be used in conjunction with change in height and mass measurements to gain understanding into the blowing and gelling reactions that occur during 
polyurethane foaming as well as give important information on cell morphology. FoamPi is an open-source Raspberry Pi device for monitoring polyurethane foaming 
reactions. The device effectively monitors temperature rise, change in foam height as well as changes in the mass during the reaction. 
Three Python scripts are also presented. The first logs raw data during the reaction. The second corrects temperature data such that it can be used in ATR 
reactions for calculating isocyanate conversion; additionally this script reduces noise in all the data and removes erroneous readings. The final script 
extracts important information from the corrected data such as maximum temperature change and maximum height change as well as the time to reach these points. 
Commercial examples of such equipment exist however the price (>£10000) of these equipment make these systems inaccessible for many research laboratories. The FoamPi 
build presented is inexpensive (£350) and test examples are shown here to indicate the reproducibility of results as well as precision of the FoamPi. 

FoamPi3.py

This script that runs on the RPI to log temperature, height, mass and time.

TempHeightCorrect.py 

This script corrects the temperature for adiabatic temperature rise, and eliminates erroneous data from all the sets of data as well as applies a 21 point moving
average.

Summary T-H-M.py

This takes all the corrected files in a folder and summarises the data, extracting important points.

