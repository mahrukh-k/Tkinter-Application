# Intermediate Python
# Ricardo Ibarra Gil
# API CDC Vaccination
# Project Team: The movers

def prep_vax_data():
    import pandas as pd
    from fips_translation.fips_v3 import FIPS_Translator
    import numpy as np
    
    # NOTE:
    # make sure to install these packages before running:
    # pip install sodapy
    
    # 1/3 Get informatoin for vaccinated population at county level from CDC's API 
    from sodapy import Socrata
    
    # The following lines code came in the documentaation of CDC API to get the vaccination information:
    
    client = Socrata('data.cdc.gov',
                      'wIDtTH09SgLyLtQVNKEUb5QbJ',
                     "ribarrag@andrew.cmu.edu",
                      "Socrata16!")
    
    # If identification fails, info can be retrieved without it
    # client = Socrata("data.cdc.gov", None)
    
    # The query should be 3282 so we only get the entries for the latest day
    results = client.get("8xkx-amqh", limit=3282)
    vaccine_df = pd.DataFrame.from_records(results)
    
    # Keep only relevant columns for analysis
    cols = vaccine_df.columns
    cols_keep = [cols[1], cols[3], cols[4], cols[5]]
    vaccine_df = vaccine_df[cols_keep]
    
    # Convert relevant column info into float instead of strings
    vaccine_df['series_complete_pop_pct'] = vaccine_df['series_complete_pop_pct'].astype(float)
    
    # CDC's API does not provide information for TEXAS. 
    # We will get information for Texas directly from its Department of Health 
    # So, I drop all rows for which the state is TX
    vaccine_df.drop(vaccine_df[vaccine_df['recip_state'] == 'TX'].index, inplace = True)
    
    # Eliminate those with unique identifier for counties (fips) is set as Unknown (UNK)
    # Those rows contain infromation for the state level, not the county level
    vaccine_df.drop(vaccine_df[vaccine_df['fips'] == 'UNK'].index, inplace = True)
    
    # Some counties have 0 (zero) in their vaccination variable, so their vaccination info is set to NAN
    vaccine_df.loc[vaccine_df['series_complete_pop_pct'] == 0,'series_complete_pop_pct'] = np.nan
    
    # ConChange scale for vaccination pct variable from 0-100 to 0-1
    vaccine_df['series_complete_pop_pct'] = vaccine_df['series_complete_pop_pct'] / 100
    
    
    ## ------------------ #### ------------------ #### ------------------ ##
    ## ------------------ #### ------------------ #### ------------------ ##
    
    # 2/3 Get information for Texan counties
    
    # Try/Except clause was added in case the Excel file is not available from Texas website.
    # It happened once, on Oct 6, at 20:00 when the Data Set was under maintenance. The Excel displayed the 
    # follwing message: "The public dashboard is undergoing maintenance to correct county-level data.
    # The full dashboard will be republished tomorrow."
    # The Excel file included is the data as downloaded on Oct 6, 2021 without any processing.
    
    try:
        URL_Texas_vac ="https://dshs.texas.gov/immunize/covid19/COVID-19-Vaccine-Data-by-County.xls"
        texas_vacc = pd.read_excel(URL_Texas_vac, sheet_name = 'By County',
                                    skiprows = range(1,4), usecols = 'A,C:I', nrows = 254)
    except:
        texas_vacc = pd.read_excel('vaxdata/OriginalDatasets/COVID-19 Vaccine Data by County.xlsx', sheet_name = 'By County',
                                    skiprows = range(1,4), usecols = 'A,C:I', nrows = 254)
    
    
    # Call for the FIPS_Translator to obtain FIPS codes (unique identifiers for counties) using only 
    # state name and county name. FIPS codes are essential for this projects as unique identifiers for counties
    fips = FIPS_Translator()
    
    # Creates  empty list to palce the FIPS indetifiers, and passes every state,county through FIPS Translator
    FIPS_TX = list()
    for i in texas_vacc['County Name'] : val = fips.encode('TX', i); FIPS_TX.append(val)
    
    # Add that column into the DataFrame
    texas_vacc['FIPS'] = FIPS_TX
    
    
    # Texas data set does not contain percentage of vaccinated, so the population for every county in 
    # Texas was obtained from the census in the form of an Excel file:
    # I need to add population and then do the division: vaccinated total / population for each county
    
    # Same try / except clause as in getting data for vaccinations in Texas. Just in case the
    # site from Census for the Excel file is not working.    
   
    try:
        URL_Texas_pop = 'https://www2.census.gov/programs-surveys/popest/tables/2010-2019/counties/totals/co-est2019-cumchg-48.xlsx'
        texas_pop = pd.read_excel(URL_Texas_pop, skiprows = range(0,5), usecols = 'A,C', nrows = 254)
    except:
        texas_pop = pd.read_excel('vaxdata/OriginalDatasets/co-est2019-cumchg-48.xlsx', skiprows = range(0,5), usecols = 'A,C', nrows = 254)
    
    # Some cleaning to the Excel file
    col_0_name = texas_pop.columns[0]
    col_1_name = texas_pop.columns[1]
    texas_pop.rename(columns = {col_0_name: 'County_long', col_1_name : 'Population'}, inplace = True)
    
    # I need to have the county names to run the FIPS Translator because this data set
    # does not have unique identifier for counties. So i must first clean the names of counties.
    # A regular expression is used to eliminate the period and the words 'County, Texas' from column County
    texas_pop['County Name'] = texas_pop['County_long'].str.extract(r'(?<=\.)(.*?)(?= County)')
    texas_pop.drop('County_long', axis = 1, inplace = True)
    
    # Then use the FIPS translator to assign FIPS unique identifier to each county
    FIPS_TX_2 = list()
    for i in texas_pop['County Name'] : val = fips.encode('TX', i); FIPS_TX_2.append(val)
    texas_pop['FIPS'] = FIPS_TX_2
    
    # Merge the population information for Texas with the vaccination information for Texas based
    # on FIPS as unique identifier for counties
    texas_df = pd.merge(texas_vacc, texas_pop, how = 'outer', on = 'FIPS')
    
    # Get the percentage of people vaccinated as vaccinations in county / populaiton in county
    texas_df['pop_vacc_pct'] = texas_df['People Fully Vaccinated'] / texas_df['Population']
    
    # Do some changes and drop some columns for the merge of Texas vaccinations with CDC vaccinations
    cols_tx = texas_df.columns
    cols_keep_tx = [cols_tx[0], cols_tx[8], cols_tx[11]]
    texas_df = texas_df[cols_keep_tx]
    texas_df['state'] = 'TX'
    
    ## ------------------ #### ------------------ #### ------------------ ##
    
    # 3/3 Merge both DataFrames (vaccination from CDC for US counties with vaccination for Texas counties)
    
    # Adjust column names
    vaccine_df.rename(columns = {'recip_county' : 'county', 'series_complete_pop_pct' : 'vaccinated_pct', 'recip_state' : 'state'}, inplace = True)
    texas_df.rename(columns = {'County Name_x' : 'county', 'FIPS' : 'fips', 'pop_vacc_pct' : 'vaccinated_pct'}, inplace = True)
    
    # Do the append
    vaccination_df = vaccine_df.append(texas_df, sort = False)
    vaccination_df['vaccinated_pct'] = vaccination_df['vaccinated_pct'].round(2)
    
    
    # vaccination_df is the data set for percentage of population vaccinated at the county level 
    # for (almost) all counties in the US. The DF contains 3224 rows and 4 columns: FIPS, county, 
    # state and vaccinated pct. It contains no information on islands and teritories, and
    # other exceptions include:
        # 5 counties in Hawaii. Hawaii does not report information
        # 8 to counties from California that do not report information
    
    return vaccination_df


def search_vax_data(fips):
    vaccination_df = prep_vax_data()
    
    try:
        return round(vaccination_df.loc[vaccination_df['fips'] == fips, 'vaccinated_pct'].values[0]*100, 2)
    except IndexError:
        return 'No Data'
