from geopy.geocoders import Nominatim

# Function to get the coordinates of a given address
def get_coordinates(facility_df):
    # Loop through the rows of the DataFrame
    for i in range(len(facility_df)):
        address = facility_df['Address'][i]
        geolocator = Nominatim(user_agent="geocoding_app")
        location = geolocator.geocode(address)
        if location:
            facility_df['Latitude'][i] = location.latitude
            facility_df['Longitude'][i] = location.longitude
        # If address is not found, set the coordinates to None
        else:
            facility_df['Latitude'][i] = None
            facility_df['Longitude'][i] = None
    return facility_df