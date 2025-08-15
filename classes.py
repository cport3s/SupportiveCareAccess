from flask import Flask
from dash import dash
import sqlalchemy
import pandas as pd
import base64
import json
from datetime import datetime, timedelta

# Classes
class server_class():
    # Flask Server initialization method
    def flask_server_init(templates, statics):
        return Flask(__name__, template_folder=templates, static_folder=statics)

    # Dash Server initialization method
    def dash_server_init(flask_server, pathname):
        return dash.Dash(__name__, server=flask_server, url_base_pathname=pathname)
    
class schemaList():
    def db_connect(db_address, state):
        # Check if schema name comes complete
        if len(state) == 2:
            state = 'TSC_'+state
        # Instantiate engine class
        engine_instance = sqlalchemy.create_engine(db_address.format(state))
        db_connection = engine_instance.connect()
        return db_connection
    
    def get_states():
        # Get all states from Provider App db
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(dbCredentials.db_address, 'Provider_App')
        query = 'SELECT st_state FROM dbo.tbl_state ORDER BY st_state;'
        query_result_df = pd.read_sql(query, db_conn)
        state_list = ['TSC_'+state for state in query_result_df['st_state']]
        # Close db connection
        db_conn.close()
        return state_list
        
    def run_query_all_states(query):
        # Declare empty dataframe
        query_global_df = pd.DataFrame()
        # Get all states from Provider App db
        state_list = schemaList.get_states()
        for state in state_list:
            # Connect to DB and get all states
            db_conn = schemaList.db_connect(dbCredentials.db_address, state)
            # Run query
            tmp_df = pd.read_sql(query, db_conn)
            # If dataframe is empty, then create columns and fill with the data from the first schema
            if query_global_df.empty:
                query_global_df = tmp_df.copy()
            else:
                # Append the temporal DF to the query_global_df
                query_global_df = pd.concat([query_global_df, tmp_df], ignore_index=True)
            # Close db connection
            db_conn.close()
        return query_global_df
    
class dbCredentials():
    username = 'sa'
    password = 'Supp)rtive209'
    # To run on ITPROG
    driver = 'SQL Server Native Client 11.0'
    hostname = 'localhost'
    # To run on WEBSVR
    #driver = 'ODBC Driver 17 for SQL Server'
    #hostname = 'WEBSVR'
    db_address = 'mssql+pyodbc://sqlsvr:61433/{}?trusted_connection=yes&driver=' + driver

class pcc_class:
    auth_client_id = 'LxGhD5OHvAS2bSjCOh9lN5AoFBoVJYf7'
    auth_password = 'uA8wTxiroRNmYXG5'
    access_token = {}
    pcc_url_base = 'https://connect.pointclickcare.com/api'
    pcc_api_url = 'https://connect.pointclickcare.com/api/public/preview1/applications/supportivecarebridge/activations?pageSize=200'
    access_token_url = 'https://connect.pointclickcare.com/auth/token'

    # Method to encode the client ID and client secret
    def encode_auth_code(self):
        plain_txt_auth = self.auth_client_id + ":" + self.auth_password
        encoded_auth = plain_txt_auth.encode('ASCII')
        base64_string = base64.b64encode(encoded_auth).decode('ASCII')
        return base64_string
    
    # Check if token exists and is valid
    def check_auth_token(self):
        # Open JSON file
        with open('pcc_access_token.json', 'r') as json_file:
            current_auth_token = json.load(json_file)
            # Get token date and parse into datetime format
            auth_token_date = datetime.strptime(current_auth_token['token_date'], '%Y-%m-%d %H:%M:%S')
            # Check auth_token_date vs current time
            time_delta = datetime.now() - timedelta(hours=1)
            # If auth_token_date is within the hour of current time, then assign current access token an return True
            if auth_token_date > time_delta:
                # Get current access token from json file
                self.access_token = {'access_token': current_auth_token['access_token'], 'expires_in': current_auth_token['expires_in']}
                return True
            else:
                return False