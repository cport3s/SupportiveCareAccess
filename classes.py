from flask import Flask
from dash import dash
import sqlalchemy

# Classes
class server_class():
    # Flask Server initialization method
    def flask_server_init(templates, statics):
        return Flask(__name__, template_folder=templates, static_folder=statics)

    # Dash Server initialization method
    def dash_server_init(flask_server, pathname):
        return dash.Dash(__name__, server=flask_server, url_base_pathname=pathname)
    
class schemaList():
    # Structure: 
    #   schema:[referral_inbox,psychology_appsheet_id,psychiatry_appsheet_id,state_usps_code,state_name]
    schemaDict = {
        'TSC_AR':['arr@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'AR', 'Arkansas'],
        'TSC_CT':['ctr@thesupportivecare.com','https://supportivecarehub.com/', 'ca63a1bf-c790-4c97-8271-de806d75ad7b', 'CT', 'Connecticut'],
        'TSC_DE':['der@thesupportivecare.com','https://supportivecarehub.com/', 'ca63a1bf-c790-4c97-8271-de806d75ad7b', 'DE', 'Delaware'],
        'TSC_FL':['flr@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'FL', 'Florida'],
        'TSC_GA':['gar@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'GA', 'Georgia'],
        'TSC_IL':['ilr@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'IL', 'Illinois'],
        'TSC_MA':['ctr@thesupportivecare.com','https://supportivecarehub.com/', 'a1c1ffc3-6d49-4d27-bba0-5e9d6ec76591', 'MA', 'Massachusetts'],
        'TSC_MD':['mdr@thesupportivecare.com','https://supportivecarehub.com/', 'bc670996-170f-465e-ae17-5a3363d62274', 'MD', 'Maryland'],
        'TSC_ME':['mer@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'ME', 'Maine'],
        'TSC_MI':['mir@thesupportivecare.com','https://supportivecarehub.com/', '89059276-eb3d-4a8d-a0b1-94bb8bd95b60', 'MI', 'Michigan'],
        'TSC_NC':['ncr@thesupportivecare.com','https://supportivecarehub.com/', '43cd224d-c098-4090-96bc-19d7c9985f0d', 'NC', 'North Carolina'],
        'TSC_NH':['ctr@thesupportivecare.com','https://supportivecarehub.com/', 'd3b65d9c-d576-499d-acc9-5d7e67adf23f', 'NH', 'New Hampshire'],
        'TSC_NJ':['njr@thesupportivecare.com','https://supportivecarehub.com/', '3183b8df-6d08-4500-bc86-4c4cf6e3b625', 'NJ', 'New Jersey'],
        'TSC_NY':['nyr@thesupportivecare.com','https://supportivecarehub.com/', '369674d6-fdaf-4c08-bc58-b9a8c44a1aee', 'NY', 'New York'],
        'TSC_OH':['ohr@thesupportivecare.com','https://supportivecarehub.com/', '4d8136f5-fa2e-4279-bd7c-f0adc9cd080d', 'OH', 'Ohio'],
        'TSC_PA':['par@thesupportivecare.com','https://supportivecarehub.com/', '00b14d0b-2578-4f02-8d60-92178734933e', 'PA', 'Pennsylvania'],
        'TSC_RI':['ctr@thesupportivecare.com','https://supportivecarehub.com/', '4f9f7200-adee-452d-ac1c-a11b627f1214', 'RI', 'Rhode Island'],
        'TSC_SC':['ctr@thesupportivecare.com','https://supportivecarehub.com/', '7d6f5715-1935-40b3-b071-a45c8b73c7c5', 'SC', 'South Carolina'],
        'TSC_TN':['tnr@thesupportivecare.com','https://supportivecarehub.com/', 'f387c1c7-a5ac-4433-a999-2daa18a00885', 'TN', 'Tennessee'],
        'TSC_TX':['txr@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'TX', 'Texas'],
        'TSC_VA':['var@thesupportivecare.com','https://supportivecarehub.com/', '23836c48-4d67-4bbb-afc2-e980b1671527', 'VA', 'Virginia'],
        'TSC_VT':['ctr@thesupportivecare.com','https://supportivecarehub.com/', '                                    ', 'VT', 'Vermont']
    }

    def db_connect(self, db_address, state):
        # Instantiate engine class
        engine_instance = sqlalchemy.create_engine(db_address.format(state))
        db_connection = engine_instance.connect()
        return db_connection
    
    def db_close(self, db_connection):
        return db_connection.close()
        
    
class dbCredentials():
    username = 'sa'
    password = 'Supp)rtive209'
    # To run on ITPROG
    driver = 'SQL Server Native Client 11.0'
    # To run on WEBSVR
    #driver = 'ODBC Driver 17 for SQL Server'
    db_address = 'mssql+pyodbc://sqlsvr:61433/{}?trusted_connection=yes&driver=' + driver