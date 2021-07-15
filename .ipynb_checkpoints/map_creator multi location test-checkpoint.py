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
add_list = []

for address in response_df['Location']:
    print(address)
    geo = geolocator.geocode(address)
    if geo != None:
        print(geo)
        lat = geo.latitude
        long = geo.longitude
        lat_list.append(lat)
        long_list.append(long)
        add_list.append(geo)
    else:
        lat_list.append('41.2705')
        long_list.append('-72.9470')
        add_list.append('West Haven, CT')
    
#break up large lines
    
for (columnName, columnData) in response_df.iteritems():
    for row in range(len(columnData)):
        cell = str(columnData.iloc[row])
        count = 0
        overall_count = 0
        if cell == None:
            response_df.at[row, columnName] = ' '
        for char in cell:
            if count >= 50 and char == ' ':
                newstring = cell[:overall_count] + '<br>' + cell[overall_count:]
                response_df.at[row, columnName] = newstring
                cell = newstring
                count = 0
            count +=1
            overall_count += 1
    
response_df['Latitude'] = lat_list
response_df['Longitude'] = long_list
response_df['Geolocated address'] = add_list

colors_dict = {'Organization':              'aqua',
                'Business':                 'blue',
                'Performance Venue':        'lime',
                'Gallery/Museum':           'pink', 
                'School/Education':         'gold',
                'Landmark/Public Space':    'green',
                'Event/Festival':           'red',
                'Artist(s) Studio/Workshop':'orange',
                'House of Worship':         'purple',
                'Library':                  'brown'}




for index, row in response_df.iterrows():

    current_geo = str(row['Geolocated address'])
    with_same_address = response_df.filter(like=current_geo, axis=0)

    if len(with_same_address) == 1:

        caption_info = f"<b>{row['Name of the place/activity you wish to add to map']}</b> <br> <b>Category:</b> {row['Category - What is it?']} <br><b>Type:</b> {row['Type']} <br><b>Location:</b> {row['Location']} <br><b>Notes:</b> {row['Notes']}" 
    
        if row['Type'] in colors_dict.keys():
    
            folium.CircleMarker(
                # Latitude, longitude for each marker
                location=[row['Latitude'], row['Longitude']],
        
                # Size, fill, color of the circle marker
                
                    radius = 10, fill=True, color=colors_dict[row['Type']], #(row['FY18.Max.Population.Count']+1)/25, fill = True, color='orange',
        
                # Text that goes into the popup or tooltip
                tooltip = caption_info 
                  
                 ).add_to(base_map)

        else:

         folium.CircleMarker(
                # Latitude, longitude for each marker
                location=[row['Latitude'], row['Longitude']],
        
                # Size, fill, color of the circle marker
                
                    radius = 10, fill=True, color='gray', #(row['FY18.Max.Population.Count']+1)/25, fill = True, color='orange',
        
                # Text that goes into the popup or tooltip
                tooltip = caption_info 
                  
                 ).add_to(base_map)

    else:

        caption_info = ''

        for row in with_same_address:

            caption_info += f"<b>{row['Name of the place/activity you wish to add to map']}</b> <br> <b>Category:</b> {row['Category - What is it?']} <br><b>Type:</b> {row['Type']} <br><b>Location:</b> {row['Location']} <br><b>Notes:</b> {row['Notes']} <br> <br>"
        
        folium.CircleMarker(
                # Latitude, longitude for each marker
                location=[row['Latitude'], row['Longitude']],
        
                # Size, fill, color of the circle marker
                
                    radius = 10*(len(with_same_address)), fill=True, color='black', #(row['FY18.Max.Population.Count']+1)/25, fill = True, color='orange',
        
                # Text that goes into the popup or tooltip
                tooltip = caption_info 
                  
                 ).add_to(base_map)



html = base_map._repr_html_()

file = open("index.html","w")
file.write(html)
file.close()