from urllib.request import urlopen
import json
import plotly.io as pio
import vaxdata.vaccination as vax
import plotly.express as px


def maps(state):

    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as h:
        counties = json.load(h)
    
    vaccination_df = vax.prep_vax_data()
    
    pio.renderers.default = 'browser'
    
    fig = px.choropleth(vaccination_df[vaccination_df['state'] == state], geojson=counties, locations='fips', color='vaccinated_pct',
                                color_continuous_scale="rdylgn",
                                range_color=(0, 1),
                                scope="usa",
                                labels={'vaccinated_pct':'Fully vaccinated'},
                                hover_data = ['county'], 
                                title = 'FULLY VACCINATED POPULATION (% OF TOTAL POPULATION): {}'.format(state)
                              )
    fig.update_geos(fitbounds = 'locations', visible = True)
    fig.update_layout(margin={"r":20,"t":50,"l":20,"b":20})
    fig.show()

