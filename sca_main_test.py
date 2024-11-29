from dash import html, Input, Output, State, dcc
from flask import render_template
from classes import server_class, schemaList, dbCredentials
from fac_stats import app_layout
import sqlalchemy
import pandas as pd
import sqlalchemy.sql
from sqlalchemy.exc import SQLAlchemyError
import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

templates = 'html_folder'
statics = 'static'
current_app = 'sca_main_app.html'
db_address = dbCredentials.db_address

# Initialize Flask Server
flask_server = server_class.flask_server_init(templates, statics)

# Define Dash App Parameters
dash_fac_query = server_class.dash_server_init(flask_server, '/dash1/')
dash_fac_stats = server_class.dash_server_init(flask_server, '/facStats/')

# Dash App Body
dash_fac_query.layout = html.Div(
    [
        html.H1("Hello from Dash 1")
    ]
)

dash_fac_stats.layout = app_layout

# --------------------------------------------Dash Callbacks
@dash_fac_stats.callback(
    Output('facility_dropdown', 'options'),
    Input('state_dropdown', 'value')
    )
def populate_facility_dropdown(fac_state):
    if fac_state == 'All':
        tmp_fac_list = list(schemaList.schemaDict.keys())
    else:
        tmp_fac_list = [fac_state]
    fac_query = '''
        SELECT
        	local_fac.facility_id,
        	local_fac.facility_name
        FROM
        	dbo.tbl_facility local_fac
        FULL JOIN
        	dbo.tbl_pcc_fac pcc_fac ON pcc_fac.fac_id = local_fac.facility_id
        WHERE
        	facility_name IS NOT NULL AND pcc_fac.pcc_active = 1
        ORDER BY
        	facility_name
	'''
    for schema in tmp_fac_list:
        # Instantiate engine class
        engine_instance = sqlalchemy.create_engine(db_address.format(schema))
        tmp_fac_dataframe = pd.DataFrame()
        fac_name_list = []
        fac_id_list = []
        # Establish connection
        try:
            connection_instance = engine_instance.connect()
            logging.info('Connected to {}'.format(schema))
            tmp_fac_dataframe = pd.read_sql(fac_query, connection_instance)
            # If list is empty, then append tmp list
            if len(fac_name_list) != 0:
                fac_name_list.append(list(tmp_fac_dataframe['facility_name']))
                fac_id_list.append(list(tmp_fac_dataframe['facility_id']))
            else:
                fac_name_list = list(tmp_fac_dataframe['facility_name'])
                fac_id_list = list(tmp_fac_dataframe['facility_id'])
            # Merge lists and cast into dictionary
            fac_name_dict = dict(zip(fac_name_list, fac_id_list))
        except SQLAlchemyError as errorMessage:
            logging.debug(errorMessage)
            pass
        try:
            # Must close connection prior to dropping the table, to avoid simultaneous connections
            connection_instance.close()
            logging.info('Closing connection to {} to get facility list'.format(schema))
        except:
            pass
    # Format dictionary for dash output
    return_dict = [{'label':k, 'value':v} for k,v in fac_name_dict.items()]
    return return_dict

# Callback to generate facility graph
@dash_fac_stats.callback(
    [
        Output('facility_upload_log_graph', 'figure'),
        Output('facility_upload_log_graph_container', 'style'),
        Output('global_facility_upload_log_graph_container', 'style')
    ],
    [
        Input('facility_dropdown', 'value'),
        Input('date_filter', 'value')
    ],
    # Pass state_dropdown as a State to prevent it from triggering callback
    State('state_dropdown', 'value'),
    prevent_initial_call=True
    )
def generate_fac_graph(local_fac_id, date_range, state):
    fac_query = '''
        SELECT
        	local_fac.facility_id,
        	local_fac.facility_name,
        	pcc_fac.pcc_facID,
        	pcc_fac.pcc_orgUid
        FROM
        	dbo.tbl_facility local_fac
        FULL JOIN
        	dbo.tbl_pcc_fac pcc_fac ON local_fac.facility_id = pcc_fac.fac_id
        WHERE
        	local_fac.facility_id = {}
    '''.format(local_fac_id)
    if date_range != '':
        date_range = (datetime.now() - timedelta(days=date_range)).strftime("%Y/%m/%d %H:%M:%S")
    # Instantiate engine class
    engine_instance = sqlalchemy.create_engine(db_address.format(state))
    # Establish connection
    try:
        connection_instance = engine_instance.connect()
        logging.info('Connected to {} to get logs'.format(state))
        # Execute query to get pcc_fac_id and pcc_orguid
        tmp_pcc_fac_dataframe = pd.read_sql(fac_query, connection_instance)
        pcc_facid = tmp_pcc_fac_dataframe['pcc_facID'][0]
        pcc_orguid = tmp_pcc_fac_dataframe['pcc_orgUid'][0]
        log_query = '''
            SELECT
            	cr_dte,
	            COUNT(pcc_upl_id) AS log_qty
            FROM
            	dbo.tbl_pcc_upl_log
            WHERE
            	facID = {} AND orgUuid = '{}' AND cr_dte > '{}' AND done_dte IS NOT NULL
            GROUP BY
            	cr_dte
            ORDER BY
            	cr_dte
        '''.format(pcc_facid, pcc_orguid, date_range)
        # Get all logs for the facility
        tmp_pcc_log_dataframe = pd.read_sql(log_query, connection_instance)
        # Create plot
        facility_upload_log_graph = make_subplots(rows = 1, cols = 1, shared_xaxes = True, shared_yaxes = True)
        # Add traces
        facility_upload_log_graph.add_trace(go.Bar(x = tmp_pcc_log_dataframe['cr_dte'], y = tmp_pcc_log_dataframe['log_qty'], name = 'Uploaded'))
        # Now query all pending logs for the facility
        pending_log_query = '''
            SELECT
            	cr_dte,
	            COUNT(pcc_upl_id) AS log_qty
            FROM
            	dbo.tbl_pcc_upl_log
            WHERE
            	facID = {} AND orgUuid = '{}' AND cr_dte > '{}' AND done_dte IS NULL
            GROUP BY
            	cr_dte
            ORDER BY
            	cr_dte
        '''.format(pcc_facid, pcc_orguid, date_range)
        tmp_pending_pcc_log_dataframe = pd.read_sql(pending_log_query, connection_instance)
        facility_upload_log_graph.add_trace(go.Bar(x = tmp_pending_pcc_log_dataframe['cr_dte'], y = tmp_pending_pcc_log_dataframe['log_qty'], name = 'Pending'))
    except SQLAlchemyError as errorMessage:
        logging.debug(errorMessage)
        pass
    try:
        # Must close connection prior to dropping the table, to avoid simultaneous connections
        connection_instance.close()
        logging.info('Closing connection to {}'.format(state))
    except:
        pass
    return facility_upload_log_graph, {'display': 'block'}, {'display': 'none'}

# Callback to generate global upload statistics
@dash_fac_stats.callback(
    Output('global_facility_upload_log_graph', 'figure'),
    Input('update_interval', 'n_intervals')
)
def global_fac_statistics(n_intervals):
    tmp_fac_list = list(schemaList.schemaDict.keys())
    all_sts_dataframe = pd.DataFrame()
    all_sts_pending_dataframe = pd.DataFrame()
    # First, query all completed logs
    query = '''
    SELECT
    	cr_dte,
        COUNT(pcc_upl_id) AS log_qty
    FROM
    	dbo.tbl_pcc_upl_log
    WHERE
    	done_dte IS NOT NULL AND cr_dte > '{}'
    GROUP BY
    	cr_dte
    ORDER BY
    	cr_dte
    '''.format((datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d %H:%M:%S"))
    for state in tmp_fac_list:
        # Connect to DB
        connection_instance = schemaList.db_connect(db_address, state)
        tmp_log_dataframe = pd.read_sql(query, connection_instance)
        if all_sts_dataframe.empty:
            all_sts_dataframe = tmp_log_dataframe.copy()
        else:
            all_sts_dataframe = pd.concat([all_sts_dataframe, tmp_log_dataframe], ignore_index = True)
        # Close DB connection
        connection_instance.close()
    # Now, query all pending logs
    query = '''
    SELECT
    	cr_dte,
        COUNT(pcc_upl_id) AS log_qty
    FROM
    	dbo.tbl_pcc_upl_log
    WHERE
    	done_dte IS NULL AND cr_dte > '{}'
    GROUP BY
    	cr_dte
    ORDER BY
    	cr_dte
    '''.format((datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d %H:%M:%S"))
    for state in tmp_fac_list:
        # Connect to DB
        connection_instance = schemaList.db_connect(db_address, state)
        tmp_log_dataframe = pd.read_sql(query, connection_instance)
        if all_sts_pending_dataframe.empty:
            all_sts_pending_dataframe = tmp_log_dataframe.copy()
        else:
            all_sts_pending_dataframe = pd.concat([all_sts_pending_dataframe, tmp_log_dataframe], ignore_index = True)
        # Close DB connection
        connection_instance.close()
    all_sts_dataframe = all_sts_dataframe.groupby('cr_dte').sum().reset_index()
    all_sts_pending_dataframe = all_sts_pending_dataframe.groupby('cr_dte').sum().reset_index()
    # Create plot
    global_fac_log_graph = make_subplots(rows = 1, cols = 1, shared_xaxes = True, shared_yaxes = True)
    # Add traces
    global_fac_log_graph.add_trace(go.Bar(x = all_sts_dataframe['cr_dte'], y = all_sts_dataframe['log_qty'], name = 'Uploaded'))
    global_fac_log_graph.add_trace(go.Bar(x = all_sts_pending_dataframe['cr_dte'], y = all_sts_pending_dataframe['log_qty'], name = 'Pending'))
    return global_fac_log_graph

# Callback to generate pending logs pie chart
@dash_fac_stats.callback(
    Output('pending_logs_sunburst_chart', 'figure'),
    Input('update_interval', 'n_intervals')
)
def pending_logs_chart(n_intervals):
    # Initialize DF
    pending_logs_dataframe = pd.DataFrame()
    # Get db schema list
    tmp_fac_list = list(schemaList.schemaDict.keys())
    for state in tmp_fac_list:
        query = '''
            SELECT 
            	dbo.tbl_facility.facility_name AS facility_name,
            	COUNT(dbo.tbl_pcc_upl_log.cl_id) AS log_qty
            FROM 
            	dbo.tbl_pcc_upl_log 
            INNER JOIN
                dbo.ClientInfoTable ON dbo.tbl_pcc_upl_log.cl_id = dbo.ClientInfoTable.ClientID 
            INNER JOIN
                dbo.tbl_pcc_fac ON dbo.tbl_pcc_upl_log.orgUuid = dbo.tbl_pcc_fac.pcc_orgUid AND dbo.tbl_pcc_upl_log.facID = dbo.tbl_pcc_fac.pcc_facID 
            INNER JOIN
                dbo.tbl_facility ON dbo.tbl_pcc_fac.fac_id = dbo.tbl_facility.facility_id
            WHERE
            	(dbo.tbl_pcc_upl_log.done_dte IS NULL) AND (dbo.tbl_pcc_upl_log.cr_dte <= CAST(DATEADD(day, -2, GETDATE()) AS Date))
            GROUP BY
            	dbo.tbl_facility.facility_name;
        '''
        # Connect to DB
        connection_instance = schemaList.db_connect(db_address, state)
        tmp_log_dataframe = pd.read_sql(query, connection_instance)
        tmp_log_dataframe['state'] = state
        if pending_logs_dataframe.empty:
            pending_logs_dataframe = tmp_log_dataframe.copy()
        else:
            pending_logs_dataframe = pd.concat([pending_logs_dataframe, tmp_log_dataframe], ignore_index = True)
        # Close DB connection
        connection_instance.close()
    # Create sunburst graph
    pending_logs_pie = px.sunburst(
        pending_logs_dataframe,
        path = ['state', 'facility_name'],
        values = 'log_qty'
        )
    pending_logs_pie.update_layout(
        margin = dict(t=3, b=3, r=3, l=3)
        )
    return pending_logs_pie

# --------------------------------------------Flask Callbacks
@flask_server.route('/')
def index():
    dcc.Interval(id = 'update_interval', interval = 3000*1000, n_intervals = 0)
    return render_template('sca_main.html')

if __name__ == '__main__':
    flask_server.run(debug=True)