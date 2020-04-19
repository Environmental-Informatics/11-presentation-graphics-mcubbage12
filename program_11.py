#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 14:10:42 2020

@author: mcubbage
"""

import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt


def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    global DataDF
    global MissingValues
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    #gross data check
    for i in range (0,len(DataDF)-1):
          if 0 > DataDF['Discharge'].iloc[i]:
             DataDF['Discharge'].iloc[i]=np.nan
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )

def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    DataDF=DataDF[startDate:endDate]
    MissingValues = DataDF["Discharge"].isna().sum()

    return( DataDF, MissingValues )


def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    DataDF=pd.read_csv(fileName, header=0, delimiter= ',')
    DataDF=DataDF.set_index('Date')
    return( DataDF )


# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }




#get daily flow for the past 5 years for both streams
ReadData('TippecanoeRiver_Discharge_03331500_19431001-20200315.txt')
DataDF, MissingValues=ClipData( DataDF,'2014-10-01', '2019-09-30') 
Tippe_5=DataDF
ReadData('WildcatCreek_Discharge_03335000_19540601-20200315.txt')
DataDF, MissingValues= ClipData( DataDF,'2014-10-01', '2019-09-30')
Wildcat_5=DataDF


#plot daily flow for both streams for the past 5 years
plt.subplot(211)
plt.plot(Tippe_5["Discharge"], 'k^', label='Tippecanoe')
plt.legend()
plt.show()
plt.ylim(1,15000)

plt.subplot(212)   
plt.plot(Wildcat_5["Discharge"], 'k+', label='Wildcat')
plt.xlabel("Date")
plt.ylim(1,15000)
plt.ylabel(".                                Discharge (cubic feet per second)")
plt.legend()

plt.savefig('daily_csf.png', dpi=96)


#read in data  
Ann_met=ReadMetrics('Annual_Metrics.csv')  
Month_met=ReadMetrics('Monthly_Metrics.csv')
tippe_met=Ann_met[Ann_met['Station']=='Tippe']
wildcat_met=Ann_met[Ann_met['Station']=='Wildcat']


#plot annual coeff of var
plt.plot(tippe_met["Coeff Var"], 'k*', label='Tippecanoe')
plt.plot(wildcat_met["Coeff Var"], 'k+', label='Wildcat')
plt.xlabel("Year")
plt.ylabel("Coefficient of Variation")
#ax=plt.gca()
#ax.set_xticklabels(np.arange(1969,2019,50))
plt.tight_layout()
plt.legend()
plt.show()

plt.savefig('coeffvar.png', dpi=96)

#plot annual tqmean
plt.plot(tippe_met["Tqmean"], 'k*', label='Tippecanoe')
plt.plot(wildcat_met["Tqmean"], 'k+', label='Wildcat')
plt.xlabel("Year")
plt.ylabel("TQMean (%)")
#ax=plt.gca()
#ax.set_xticklabels(np.arange(1969,2019,50))
plt.tight_layout()
plt.legend()
plt.savefig('tqmean.png', dpi=96)

#plot annual RBrichards baker flashiness index  


plt.plot(tippe_met["R-B Index"], 'k*', label='Tippecanoe')
plt.plot(wildcat_met["R-B Index"], 'k+', label='Wildcat')
plt.xlabel("Year")
plt.ylabel("Richards Baker Flashiness Index")
#ax=plt.gca()
#ax.set_xticklabels(np.arange(1969,2019,50))
plt.tight_layout()
plt.legend()
plt.show()
plt.savefig('rbindex.png', dpi=96)


#calculate exceedence probability

ep_tippe=tippe_met.drop(columns=['site_no', 'Mean Flow', 'Median Flow', 'Coeff Var', 'Skew', 'Tqmean', 'R-B Index', '7Q', '3xMedian'])
tippe_flow=ep_tippe.sort_values('Peak Flow', ascending=False)
tippe_ranks1=stats.rankdata(tippe_flow['Peak Flow'], method='average')
tippe_ranks2=tippe_ranks1[::-1]
tippe_ep=[(tippe_ranks2[i]/(len(tippe_flow)+1)) for i in range(len(tippe_flow))]


ep_wild=wildcat_met.drop(columns=['site_no', 'Mean Flow', 'Median Flow', 'Coeff Var', 'Skew', 'Tqmean', 'R-B Index', '7Q', '3xMedian'])
wild_flow=ep_wild.sort_values('Peak Flow', ascending=False)
wild_ranks1=stats.rankdata(wild_flow['Peak Flow'], method='average')
wild_ranks2=wild_ranks1[::-1]
wild_ep=[(wild_ranks2[i]/(len(wild_flow)+1)) for i in range(len(wild_flow))]

#plot exceeedence probability
plt.plot(tippe_ep, tippe_flow['Peak Flow'], label='Tippecanoe', color='black')
plt.plot(wild_ep, wild_flow['Peak Flow'], label='Wildcat')
plt.xlabel("Exceedence Probability")
plt.ylabel("Peak Discharge (CFS)")
plt.tight_layout()
plt.legend()
plt.show()


plt.savefig('exceedence.png', dpi=96)












