#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 12:03:31 2021

@author: lweiser
"""

import pandas as pd

def get_crimedata(fips):
    #create dataframe
    crimedata = pd.read_csv("crimedata/crimeData.csv")

    #print(crimedata)

    #drops unneeded columns
    crimedata.drop("SUM", inplace = True, axis = 1)
    crimedata.drop("POP", inplace = True, axis = 1)

    #turns FIPS into strings
    for i in crimedata["FIPS"]:
        i = int(i)

    #print(crimedata.values)

    try:
        return crimedata.loc[crimedata['FIPS'] == int(fips), 'RATE'].values[0]
    except IndexError:
        return 'No Data'

