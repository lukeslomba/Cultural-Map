import requests
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from flask import Flask

base_map = folium.Map(location=[41.26, -72.95], zoom_start=13.3)

url = 'https://docs.google.com/spreadsheets/d/1EyIJRnLrWkeAJuxLVBxO2eSBMfKiQ2aHYLS3PLvQLLs/export?format=csv'
r = requests.get(url, allow_redirects=True)

open('responses.csv', 'wb').write(r.content)

response_df = pd.read_csv("responses.csv")

geolocator = Nominatim(user_agent="Luke's mapping app", timeout=2)

lat_list = []
long_list = []

for address in response_df['Location']:
    print(address)
    geo = geolocator.geocode(address)
    print(geo)
    lat = geo.latitude
    long = geo.longitude
    lat_list.append(lat)
    long_list.append(long)
    
response_df['Latitude'] = lat_list
response_df['Longitude'] = long_list

for index, row in response_df.iterrows():
    
    caption_info = row['Name'] + "<br> - Category: " + row['Category'] + "<br> - Type: " + row['Type']+"<br> - Location: " + row['Location'] + "<br> - Notes: " + row['Notes'] 
    
    folium.CircleMarker(
                # Latitude, longitude for each marker
                location=[row['Latitude'], row['Longitude']],
        
                # Size, fill, color of the circle marker
                radius = 10, fill=True, color='orange', #(row['FY18.Max.Population.Count']+1)/25, fill = True, color='orange',
        
                # Text that goes into the popup or tooltip
                tooltip = caption_info 
                  
                 ).add_to(base_map)

html = base_map._repr_html_()

file = open("index.html","w")
file.write(html)
file.close()