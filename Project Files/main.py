import os
import tkinter as tk
from tkinter import mainloop, ttk
import re
from fips_translation.fips_v3 import FIPS_Translator
import healthdata.healthdata as health
import vaxdata.vaccination as vax
import rentdata.get_rent as rent
import crimedata.get_crimerate as crime
import vaxdata.maps as map


#Initialize the FIPS translator.
#Assigning this to a class allows me to keep the translation dictionaries in memory as a local variable,
#prevents us from needing to scrape the website for every translation pass
fips = FIPS_Translator()


def fetchdata():
    """
    Method called when the "search data" button is pressed.
    Encodes the state and county input into a FIPS code and passes that to the search functions for each dataset processing module.
    Updates the 4 lables at the bottom of the window to show returned data.
    """
    #get contents from the state and county entry feilds
    state = stateinp.get()
    county = countyinp.get()

    #convert state and county to FIPS
    #(most of the input cleaning is handled in the Fips translator module)
    code = fips.encode(state, county)

    #gets data to display in the labels at the bottom of the window
    healthdata = f'Pop per primary care physician: {health.return_healthdata(code)}'
    vaxdata = f'Percent of pop fully vaccinated: {vax.search_vax_data(code)}'
    rentdata = f'Median monthly rent (USD): {rent.medianrent(code)}'
    crimedata = f'Crimes per 100,000 hab: {crime.get_crimedata(code)}'

    #updates lables to display data
    opt1.config(text = healthdata)
    opt2.config(text = vaxdata)
    opt3.config(text = rentdata)
    opt4.config(text = crimedata)


def showcounties():
    #Method that calls the map function to display a map of county vaccination percentages
    #Only takes the input from the state feild, ignores everything else
    state = stateinp.get()
    if len(state) > 2:
        state = fips.state_to_abr(state)
    map.maps(state.upper())


if __name__ == '__main__':
    #Tkinter code that sets up the main window display loop and arranges all of the display elements
    main = tk.Tk()
    tk.Label(main, text ='State').grid(row=0)
    tk.Label(main, text = 'County').grid(row=1)
    opt1 = tk.Label(main)
    opt1.grid(row=5)
    opt2 = tk.Label(main)
    opt2.grid(row=6)
    opt3 = tk.Label(main)
    opt3.grid(row=7)
    opt4 = tk.Label(main)
    opt4.grid(row=8)
    stateinp = tk.Entry(main)
    countyinp = tk.Entry(main)

    stateinp.grid(row=0, column=1)
    countyinp.grid(row=1, column=1)

    #Sets up buttons. Each one is linked to a seperate method written above that is run when that button is pressed
    tk.Button(main, text = 'Search and Display information', command = fetchdata).grid(row=3, column=0)
    tk.Button(main, text = 'Display State Map (vaccinated pop)', command = showcounties).grid(row=4, column=0)

    #runs mainloop to display the GUI
    tk.mainloop()