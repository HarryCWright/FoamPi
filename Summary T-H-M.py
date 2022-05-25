# -*- coding: utf-8 -*-

import csv, glob,numpy, os
from tkinter import Tk
from tkinter.filedialog import askdirectory

root = Tk()
root.withdraw()
path = askdirectory(title='Select Folder')

os.chdir(path)


filelist = glob.glob("*.csv")

CSVout = 'ATRsumm.csv'
with open(CSVout,'w', newline='') as f: 
    head = ['Sample','DelTraw', 'DelTmax', 'tTmax', 'Hmax','tHmax','Hfin','SagH']
    csvwrite = csv.DictWriter(f,fieldnames = head)
    csvwrite.writeheader()


for file in filelist:
    
    time, Traw, DelT, H, Tj, T = [], [], [], [], [], []
#grabs data from the current csv   
    with open(file,'rt') as csvfile:
        csvRead = csv.reader(csvfile,delimiter=',')
        csvfile.readline()
        for row in csvRead:
            time.append(float(row[0]))
            T.append(float(row[3]))
            Traw.append(float(row[2]))
            Tj.append(float(row[1]))
            H.append(float(row[5]))

    
    sample = file.split('_')[0]
    print (sample)
    DelTmax = numpy.amax(T)-numpy.average(Tj)
    DelTraw = numpy.amax(Traw)-numpy.average(Tj)
    Tmax    = numpy.amax(T) 
    Hmax     = numpy.amax(H)
    Hfin     = numpy.average(H[-200:-50])
    Sag   = (Hmax-Hfin)


    k = [i for i,x in enumerate(H) if x > 0.98* Hmax][0]
    l = [i for i,x in enumerate(T) if x > 0.98*numpy.amax(T)][0] 

    
    tH  = time[k]
    tTmax = time[l]

 
    
    with open(CSVout,'a', newline='') as f:
        head =     head = ['Sample','DelTraw', 'DelTmax', 'tTmax', 'Hmax','tHmax',
                           'Hfin','SagH']
        csvwrite = csv.DictWriter(f,fieldnames = head)
        csvwrite.writerow({'Sample': sample, 'DelTraw': DelTraw, 'DelTmax': DelTmax,
                           'tTmax': tTmax, 'Hmax': Hmax, 
                           'tHmax': tH, 'Hfin': Hfin,'SagH': Sag})