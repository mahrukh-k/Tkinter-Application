# -*- coding: utf-8 -*-
"""
Median Rent by U.S County

@author: Mahrukh Khan (mahrukhk)
"""

def medianrent(fips_code):
    import pandas as pd
    
    #url=https://data.census.gov/cedsci/table?q=S25&g=0100000US%240500000&d=ACS%201-Year%20Estimates%20Subject%20Tables&tid=ACSST1Y2018.S2506&hidePreview=false
    #median rent is in the VALUES tab on the website.
    #column in csv: B25064_001E
    
    #create dataframe
    rentdata = pd.read_csv("rentdata/ACSDT5Y2019.B25064_data_with_overlays_2021-10-07T124104.csv")
    
    #remove label row from data
    rentdata = rentdata.iloc[1: , :]
    
    #change name of rent column
    rentdata.rename(columns={'B25064_001E' : 'Median Rent ($)'}, inplace = True)
    
    #extract FIPS from GEO_ID
    fips = rentdata['GEO_ID'][-6:]
    
    fips = rentdata['GEO_ID'].str.split('US')
    fips_ = []
    for x in fips:
        fips_.append(x[1])
    
    #add extracted fips to rent dataframe
    rentdata['fips'] = fips_
    rentdata.rename(columns={'B25064_001E' : 'Median Rent ($)'}, inplace = True)
    
    #clean rent column and convert to float because it has a dash which makes it a string
    rentdata['Median Rent ($)'].replace({'-': None}, inplace = True)
    
    rentdata['Median Rent ($)'] = rentdata['Median Rent ($)'].astype(float)
    
    #extract relevant data
    medianrent_df = rentdata[['fips', 'Median Rent ($)']]
    
    try:
        return (medianrent_df.loc[medianrent_df['fips'] == fips_code, 'Median Rent ($)']).values[0]
    except IndexError:
        return 'No data'
