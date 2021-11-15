import requests
import folium
import pandas as pd
from geopy.geocoders import Nominatim
from flask import Flask

def descriptionize(row):
    
    output = f"<b>{row['Name of the place/activity you wish to add to map']}</b> <br> <b>Category:</b> {row['Category - What is it?']} <br><b>Type:</b> {row['Type']} <br><b>Location:</b> {row['Location']} <br><b>Notes:</b> {row['Notes']}<br> <b>What do you love/appreciate about it?:</b><br>{row['What do you love/appreciate about it?']}"
    return output

def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map

'''
# DOWNLOAD DATA FROM GOOGLE SHEET TO LOCAL CSV FILE

url = 'https://docs.google.com/spreadsheets/d/1EyIJRnLrWkeAJuxLVBxO2eSBMfKiQ2aHYLS3PLvQLLs/export?format=csv'
r = requests.get(url, allow_redirects=True)

open('responses.csv', 'wb').write(r.content)
'''

# IMPORT DATASET FROM LOCAL CSV FILE

response_df = pd.read_csv("coded_responses.csv")

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

response_df.to_csv('coded_responses.csv')

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


# OFFSET ASSETS AT THE SAME LOCATION

df = response_df.copy()
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
                'School/Education':         'magenta',
                'Landmark/Public Space':    'green',
                'Event/Festival':           'red',
                'Artist(s) Studio/Workshop':'orange',
                'House of Worship':         'purple',
                'Library':                  'brown',
                'Other':                    'grey'}

for i in range(len(df)):
    if df.loc[i, 'Type'] in colors_dict.keys():
        df.loc[i, 'Color'] = colors_dict[df.loc[i, 'Type']]
    else:
        df.loc[i, 'Color'] = 'gray'
            
# MAKE THE MAP
            
base_map = folium.Map(location=[41.26, -72.95], zoom_start=13.3)

df.fillna('', inplace=True) #replace nan values with empty string

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
    
# ADD LEGEND TO MAP

base_map = add_categorical_legend(base_map, 'Asset type',
                             colors = list(colors_dict.values()),
                           labels = list(colors_dict.keys()))
'''
# SAVE MAP TO HTML FILE
        
html = base_map._repr_html_()

file = open("index.html","w")
file.write(html)
file.close()
'''

base_map