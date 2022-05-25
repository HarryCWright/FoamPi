# -*- coding: utf-8 -*-


from __future__ import division
import csv, numpy, glob, os
import matplotlib.pyplot as plt
from scipy import integrate
from tkinter import Tk
from tkinter.filedialog import askdirectory

def findmax(InArr):
    Amax = max(InArr)
    iMax = [i for i,x in enumerate(InArr) if x == Amax]
    iMax = iMax[0]
    return Amax, iMax

def findslope(t,T):
    mc,res,_,_,_ = numpy.polyfit(t,T,1,full = True)
    return mc, res

# calculates the rsquared of a set of values given y and mean
def r2(y,yhat):
    y2 = []
    yhat2 = []
    yavg = numpy.mean(y)
    y2[:] = [(y[x]-yavg)**2 for x in range(len(y))]
    yhat2[:] = [(yhat[x]-yavg)**2 for x in range(len(yhat))]
    sst = sum(y2)
    ssr = sum(yhat2)
    rsq = ssr/sst
    return rsq

def U(tin,Tin,Tamb):
    lnTfit =[]
    Tmax, iTmax = findmax(Tin)
    iStart      = round((len(Tin) - iTmax)/2) + iTmax
    fitt        = tin[iStart:]
    Trawfit     = Tin[iStart:]
    Trawfit[:]  = [Trawfit[x]-Tamb[x] for x in range(len(Trawfit))]
    Tln         = numpy.log(Trawfit)
    eq, R       = findslope(fitt,Tln)
    lnTfit[:]   = [fitt[x]*eq[0]+eq[1] for x in range(len(fitt))]
    rsq         = r2(Tln,lnTfit)
    return eq[0], lnTfit, rsq
    
def Simp(U,T,Tamb,t):
    Tcorr, Tdif = [], []
    Tdif[:]  = [T[x]-Tamb[x] for x in range(len(T))]
    for k in range(len(T)):
        Tadj = 0
        if k > 2:
            Tadj = -U*integrate.simps(Tdif[0:k],t[0:k])
        Tcorr.append(T[k]+Tadj)
    return Tcorr

def mvAvg(Val,pt):
    num = int((pt-1)/2)
    Val2 = []
    for k in range(len(Val)):
        if k > num and k < ((len(Val)-1)-num):
            Val2.append(numpy.mean(Val[(k-num):(k+num)]))
        else:
            Val2.append(Val[k])
    return Val2
        
def dxdt(Val,t):
    dvaldt = []
    for k in range(len(Val)):
        if k > 0:
            dvaldt.append((Val[k]-Val[k-1])/(t[k]-t[k-1]))
        else:
            dvaldt.append(0)
    return dvaldt
            
root = Tk()
root.withdraw()
path = askdirectory(title='Select Folder')

os.chdir(path)

#Glob finds all csvs and opens them
for file in glob.glob("*.csv"):
    
    print(file)
    
#Raw data arrays, used to hold data from thee CSV   
    t = []
    Traw, Tjraw =[], []
    Tdif = []
    Hraw= []
    Hraw2 = []
    
#Reads the data from the current CSV and stores data in arrays
    with open(file,'rt') as csvfile:
        csvRead = csv.reader(csvfile,delimiter=',')
        csvfile.readline()
        for row in csvRead:
            t.append(float(row[0]))
            Traw.append(float(row[1]))
            Tjraw.append(float(row[2]))
            Hraw.append(float(row[3]))
    Hraw2[:] = Hraw[:]
           
#Get the slopes of ln(T-Tamb), U heat transfer coefficient
# fit as well as actual fit and rsq
    U1, Tfit1, rsq1 = U(t, Traw, Tjraw)
    
    #print (rsq1, rsq2, rsq3)
#Use Simpsons law to integrate and correct for heat loss in temperature
    
    Tcorr = Simp(U1,Traw,Tjraw,t)

    Hraw   = mvAvg(Hraw,21) 
#fix the initial height measurement by fitting straight line
    dH1dt = []
    exc =[]
    for l in range(len(Hraw)):
        if l>20:
            if Hraw[l] < 0:
                Hraw[l] = Hraw[l-1]
            elif Hraw[l] > 2*Hraw[l-1] and Hraw[l] > 50:
                Hraw[l] = Hraw[l-1]
            elif Hraw[l] < 0.5*Hraw[l-1] and Hraw[l] > 50:
                Hraw[l] = Hraw[l-1]
    
           
    for l in range(len(Hraw)):            
        if l > 0:
            dH1dt.append(((Hraw[l]-Hraw[l-1])/(t[l]-t[l-1]))**2)
        else:
            dH1dt.append(0)
 
    lim = 500
    for k in range(200):
        if dH1dt[k] > lim:
            exc.append(k)
       # exc = [i for i,x in enumerate(dH1dt) if x > lim]

        
    if len(exc)>0:
        mfit = (Hraw[exc[-1]+2]-Hraw[exc[0]-2])/(t[exc[-1]+2]-t[exc[0]-2])
        cfit = Hraw[exc[0]-2] - mfit * t[exc[0]-2]
        
        for z in range(exc[0]-2,exc[-1]+2):
            Hraw[z] = mfit*t[z]+cfit

    
       
        
#Apply a 21 point moving average to the outputs
    Tcorr  = mvAvg(Tcorr,21)
    Hcorr   = mvAvg(Hraw,21)
    
#Get dx/dt for each of the responses
    dTdt   = dxdt(Tcorr,t)
    dHdt    = dxdt(Hcorr,t)
    
#Figures out the File name and where to split
    name = file.split('.')
    if len(name) == 3:
        nameout = name[0]+name[1]
    else: nameout = name[0]
    
#Writing all the Data to a CSV
    CSVout = nameout+ "_Corrected.csv"    
    with open(CSVout,'w', newline='') as f: 
        head = ['t', 'Tj','Traw','Tcorr', 'Hraw', 'Hcorr','dTdt', 'dHdt']
        csvwrite = csv.DictWriter(f,fieldnames = head)
        csvwrite.writeheader()
        for j in range(len(t)):
            csvwrite.writerow({'t': t[j], 'Tj': Tjraw[j], 'Traw': Traw[j], 
                               'Tcorr': Tcorr[j], 'Hraw': Hraw[j], 'Hcorr': Hcorr[j],
                               'dTdt': dTdt[j], 'dHdt': dHdt[j]})
    
    
#Code for plotting the data if needed
    pltT = 'Y'
    if pltT == 'Y' :
        
        fig = plt.figure(figsize=(10,12))
        
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        
        ax1.plot(t,Tcorr)
        ax1.plot(t,Traw)
        ax1.set_xlabel('time (s)',fontsize =20)
        ax1.set_ylabel('T1 /$^\circ$C',fontsize =20)
        ax1.set_xlim(0,800)
        ax1.set_ylim(bottom = 0)
    
        ax2.plot(t,Hraw2)
        ax2.plot(t,Hcorr)
        ax2.set_xlabel('time (s)',fontsize =20)
        ax2.set_ylabel('Height /mm',fontsize =20)
        ax2.set_xlim(0,800)
        ax2.set_ylim(0,200)
    
        
        
        plt.savefig(nameout+'.png')
        plt.close()
    