from geopy.geocoders import Nominatim
from classes import schemaList
import pandas as pd
import time
import json
from datetime import datetime

# Function to get the coordinates of a given address
def get_coordinates(facility_df):
    facility_df['Latitude'] = ''
    facility_df['Longitude'] = ''
    geolocator = Nominatim(user_agent="geocoding_app")
    # Loop through the rows of the DataFrame
    for i in range(len(facility_df['facility_name'])):
        address = facility_df['facility_address'][i]
        location = geolocator.geocode(address)
        current_date = datetime.now().strftime('%Y-%m-%d')
        if location:
            facility_df['Latitude'][i] = location.latitude
            facility_df['Longitude'][i] = location.longitude
        # If address is not found, set the coordinates to None
        else:
            facility_df['Latitude'][i] = None
            facility_df['Longitude'][i] = None
        with open('facility_coordinates.json', 'a') as j:
            json.dump({facility_df['facility_name'][i], address, facility_df['Latitude'][i], facility_df['Longitude'][i], current_date}, j)
            print(i, facility_df['facility_name'][i], address, facility_df['Latitude'][i], facility_df['Longitude'][i], current_date)
        # Insert 1 second timer due to geopy usage policy
        time.sleep(60)
    # Save dataframe to json file
    facility_df.to_json('facility_coordinates.json', orient='records')
    return facility_df

# Function to get all facilities addresses
def get_fac_address():
    query = '''
    SELECT 
        facility_name, 
        CONCAT(facility_street, ', ', facility_city, ', ', RIGHT(DB_NAME(), 2)) AS facility_address
    FROM
        dbo.tbl_facility
    '''
    # Run query
    facility_df = schemaList.run_query_all_states(query)
    # Save facility df as a csv file with the current date as filename
    current_date = datetime.now().strftime('%Y-%m-%d')
    facility_df.to_csv(f'facility_addresses_{current_date}.csv', index=False)
    facility_df = get_coordinates(facility_df)
    return facility_df

get_fac_address()