import os
import pandas as pd


def load_data():
    #loads the dataset from the csv
    data = pd.read_csv('healthdata/analytic_data2021.csv', low_memory=False).drop(index=0)
    return data

def return_healthdata(fips, data = load_data()):
    """
    Searches dataset to return primary care physicians per capita
    Also takes raw dataset as an input if the dataset is already in memory somewhere, otherwise it will just load the dataset when called
    """
    #searches through dataset to find row for corresponding FIPS code
    out = data.loc[data['5-digit FIPS Code'] == str(fips)]
    #returns cell from the proper column
    out = out['Ratio of population to primary care physicians.']
    
    #handles keyerrors so the program still outputs when a blank cell is returned
    try:
        #returns rounded value of the cell
        return round(float(out.values[0]), 2)
    except IndexError:
        return 'No Data'