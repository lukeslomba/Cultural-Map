import requests
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from flask import Flask

def descriptionize(row):
    
    output = f"<b>{row['Name of the place/activity you wish to add to map']}</b> <br> <b>Category:</b> {row['Category - What is it?']} <br><b>Type:</b> {row['Type']} <br><b>Location:</b> {row['Location']} <br><b>Notes:</b> {row['Notes']}<br> <b>What do you love/appreciate about it?:</b><br>{row['What do you love/appreciate about it?']}"
    return output

'''
# DOWNLOAD DATA FROM GOOGLE SHEET TO LOCAL CSV FILE

url = 'https://docs.google.com/spreadsheets/d/1EyIJRnLrWkeAJuxLVBxO2eSBMfKiQ2aHYLS3PLvQLLs/export?format=csv'
r = requests.get(url, allow_redirects=True)

open('responses.csv', 'wb').write(r.content)
'''

# IMPORT DATASET FROM LOCAL CSV FILE

response_df = pd.read_csv("responses.csv")

geolocator = Nominatim(user_agent="Luke's mapping app", timeout=2)

lat_list = []
long_list = []
add_list = []

for address in response_df['Location']:
    #print(address)
    geo = geolocator.geocode(address)
    if geo != None:
        #print(geo)
        lat = geo.latitude
        long = geo.longitude
        lat_list.append(lat)
        long_list.append(long)
        add_list.append(geo)
    else:
        lat_list.append('41.2705')
        long_list.append('-72.9470')
        add_list.append('West Haven, CT')
    
# BREAK UP LARGE LINES OF STRING DATA (for better display in popup)
    
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


# REPLACE NaN VALUES WITH EMPTY STRING

df = response_df.copy()
df.fillna('', inplace=True)

# OFFSET ASSETS AT THE SAME LOCATION

unique_addresses = df.drop_duplicates(subset = ['Latitude', 'Longitude'])

print(df.equals(unique_addresses))

c = 0.0005
lat_dict = {0: 0, 1: -c, 2: c, 3: 0, 4: 0, 5: -c, 6: -c, 7: c, 8: c, 9: -2*c, 10: 2*c}
long_dict = {0: 0, 1: 0, 2: 0, 3: -c, 4: c, 5: c, 6: c, 7: -c, 8: c, 9: 0, 10: 0}

print(lat_dict)

for index, row in unique_addresses.iterrows():
    #print(row)
    current_lat = row['Latitude']
    current_long = row['Longitude']

    same_loc_df = df.loc[(df['Latitude'] == current_lat) & (df['Longitude'] == current_long)]
    
    if len(same_loc_df) > 1:

        count = 0    
        for index, row in same_loc_df.iterrows():
            #print(index)
            old = float(df.at[index,'Latitude'])
            df.at[index,'Latitude'] = float(df.at[index,'Latitude']) + 0.7*lat_dict[count]
            df.at[index,'Longitude'] = float(df.at[index,'Longitude']) + long_dict[count]
            count += 1

# ASSIGN COLORS TO BUBBLES

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

for i in range(len(df)):
    if df.loc[i, 'Type'] in colors_dict.keys():
        df.loc[i, 'Color'] = colors_dict[df.loc[i, 'Type']]
    else:
        df.loc[i, 'Color'] = 'gray'
            
# MAKE THE MAP
            
base_map = folium.Map(location=[41.26, -72.95], zoom_start=13.3)

for index, row in df.iterrows():
    
    caption_info = descriptionize(row)#['Popup label']
    
    folium.CircleMarker(
                # Latitude, longitude for each marker
                location=[row['Latitude'], row['Longitude']],
        
                # Size, fill, color of the circle marker
                
                radius = 10, fill=True, color=row['Color'], #(row['FY18.Max.Population.Count']+1)/25, fill = True, color='orange',
        
                # Text that goes into the popup or tooltip
                tooltip = caption_info 
                  
                 ).add_to(base_map)
      
# SAVE MAP TO HTML FILE
        
html = base_map._repr_html_()

file = open("index.html","w")
file.write(html)
file.close()

