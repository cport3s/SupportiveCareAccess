from flask import Flask
from dash import dash
import sqlalchemy
import pandas as pd

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
        state_list_df = schemaList.get_states()
        for state in state_list_df['st_state']:
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
    # To run on WEBSVR
    #driver = 'ODBC Driver 17 for SQL Server'
    db_address = 'mssql+pyodbc://sqlsvr:61433/{}?trusted_connection=yes&driver=' + driver