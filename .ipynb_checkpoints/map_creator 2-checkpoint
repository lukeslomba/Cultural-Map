import requests
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from flask import Flask

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


def descriptionize(row):
    
    output = f"<b>{row['Name of the place/activity you wish to add to map']}</b> <br> <b>Category:</b> {row['Category - What is it?']} <br><b>Type:</b> {row['Type']} <br><b>Location:</b> {row['Location']} <br><b>Notes:</b> {row['Notes']}<br> <b>What do you love/appreciate about it?:</b><br>{row['What do you love/appreciate about it?']}"
    return output


def condense_duplicates(df):
    
    #df['Popup label'] = pd.Series(dtype='str')
    #df['Size'] = pd.Series(dtype='str')
    
    locations = []
    sizes = []
    droplist = []
    
    for i in range(len(df)):
            
            current_add = df.loc[i, 'Geolocated address']
            
            if current_add in locations:
                droplist.append('yes')
                
                target_row = df[df['Geolocated address'] == current_add].iloc[0]
                
                target_index = df[df['Geolocated address'] == current_add].index.tolist()[0]
                
                df.loc[target_index, 'Popup label'] += ('<br><br>' + descriptionize(df.iloc[i]))
                
                df.loc[target_index, 'Size'] += 2
                
                df.loc[target_index, 'Color'] = 'black'
                
            else:
                droplist.append('no')
                
                df.loc[i, 'Popup label'] = descriptionize(df.iloc[i])
                
                df.loc[i, 'Size'] = 10
                
                if df.loc[i, 'Type'] in colors_dict.keys():
                    df.loc[i, 'Color'] = colors_dict[df.loc[i, 'Type']]
                else:
                    df.loc[i, 'Color'] = 'gray'
            
            locations.append(current_add)
            
    df['Drop?'] = droplist
    
    drop_indexes = df[df['Drop?'] == 'yes'].index.tolist()
    
    print(drop_indexes)
    
    df = df.drop(drop_indexes).reset_index()        

    return df


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

response_df = condense_duplicates(response_df)

for index, row in response_df.iterrows():
    
    caption_info = row['Popup label']
    
    folium.CircleMarker(
                # Latitude, longitude for each marker
                location=[row['Latitude'], row['Longitude']],
        
                # Size, fill, color of the circle marker
                
                    radius = row['Size'], fill=True, color=row['Color'], #(row['FY18.Max.Population.Count']+1)/25, fill = True, color='orange',
        
                # Text that goes into the popup or tooltip
                tooltip = caption_info 
                  
                 ).add_to(base_map)


html = base_map._repr_html_()

file = open("index.html","w")
file.write(html)
file.close()
