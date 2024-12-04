from dash import Dash, html, dcc, dash_table, Input, Output, State, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import sqlalchemy
import sqlalchemy.sql
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dash_styles import nav_bar, content
from sca_functions import suppcare_header
from classes import schemaList, dbCredentials
from dash_styles import SuppCareBanner
import logging

db_address = dbCredentials.db_address

main_app = Dash(__name__, title='SupportiveCare Access Portal', external_stylesheets=[dbc.themes.BOOTSTRAP])
main_server = main_app.server

#---------------------------------------------LAYOUT
main_app.layout = html.Div(
    children = [
        # Works in conjunction with "active=exact" in the navlink item. Marks active items in the nav menu
        dcc.Location(id='current_url'),
        suppcare_header(),
        dbc.Nav(
            id='nav_menu_container',
            children=[
                dbc.NavLink('Patient Info', href='/patients_info', active='exact'),
                dbc.NavLink('Provider Info', href='/prov_info', active='exact'),
                dbc.NavLink('Facility Info', href='/fac_info', active='exact'),
                dbc.NavLink('Facility Statistics', href='/fac_stats', active='exact')
            ],
            vertical=True,
            pills=True,
            style=nav_bar.SIDEBAR_STYLE
        ),
        # App container, will be updated based on url
        html.Div(
            id='fac_stats_container',
            style=content.FAC_STATS_STYLE,
            children = [
                html.Div(
                    id = 'facility_dropdown_container',
                    children = [
                        dcc.Dropdown(
                            id = 'state_dropdown',
                            placeholder='State'
                        ),
                        dcc.Dropdown(
                            id = 'facility_dropdown',
                            disabled=True,
                            placeholder='Select a State First..'
                        ),
                        dcc.Dropdown(
                            id = 'date_filter',
                            options = [
                                {'label': '7 days', 'value': 7},
                                {'label': '30 days', 'value': 30},
                                {'label': '90 days', 'value': 90},
                                {'label': '360 days', 'value': 360},
                                {'label': 'All', 'value': ''}
                            ],
                            value = ''
                        )
                    ]
                ),
                html.Div(
                    id = 'facility_upload_log_graph_container',
                    style = {'display': 'none'},
                    children = [
                        dcc.Graph(
                            id = 'facility_upload_log_graph'
                        )
                    ]
                ),
                html.Div(
                    id = 'global_facility_upload_log_graph_container',
                    style = {'display': 'block'},
                    children = [
                        dcc.Graph(
                            id = 'global_facility_upload_log_graph'
                        )
                    ]
                ),
                html.Div(
                    id = 'pending_logs_sunburst_chart_container',
                    style = {'display': 'block'},
                    children = [
                        dcc.Graph(
                            id = 'pending_logs_sunburst_chart'
                        )
                    ]
                )
        ]
        ),
        html.Div(
            id='patient_container',
            style=content.PATIENT_STYLE,
            children = [
                html.P('This is a test')
            ]
        ),
        dcc.Interval(
            id = 'update_interval',
            interval = 3000*1000,
            n_intervals = 0
        )
    ]
)

#-------------------------------------------CALLBACKS
@main_app.callback(
    [
        Output('fac_stats_container', 'style'),
        Output('patient_container', 'style')
    ],
    Input('current_url', 'pathname')
)
def render_container(pathname):
    # Change containers display properties depending on URL
    fac_stats_style_dic = content.FAC_STATS_STYLE
    patient_style_dic = content.PATIENT_STYLE
    if pathname == '/fac_stats':
        fac_stats_style_dic['display']='block'
        patient_style_dic['display']='none'
    elif pathname == '/patients_info':
        fac_stats_style_dic['display']='none'
        patient_style_dic['display']='block'
    else:
        fac_stats_style_dic['display']='none'
        patient_style_dic['display']='none'
    return fac_stats_style_dic, patient_style_dic

# Callback to populate the state dropdown
@main_app.callback(
    Output('state_dropdown', 'options'),
    Input('current_url', 'pathname')
    )
def populate_facility_dropdown(pathname):
    if pathname == '/fac_stats':
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, 'Provider_App')
        query = 'SELECT st_id,st_state FROM dbo.tbl_state ORDER BY st_state;'
        query_result_df = pd.read_sql(query, db_conn)
        query_result_dict = dict(zip(list(query_result_df['st_id']), list(query_result_df['st_state'])))
        # Give format for dash dropdowns
        return_dict = [{'label':[state+' | ID: ',id], 'value': 'TSC_'+state} for id,state in query_result_dict.items()]
        # Close db connection
        db_conn.close()
        return return_dict
    else:
        raise PreventUpdate
    
# Callback to populate the "Facility" dropdown menu with all facilty names
@main_app.callback(
    [
        Output('facility_dropdown', 'options'),
        Output('facility_dropdown', 'disabled')
    ],
    Input('state_dropdown', 'value'),
    prevent_initial_call=True
    )
def populate_facility_dropdown(fac_state):
    fac_query = '''
        SELECT

        	local_fac.facility_id AS fac_id,
        	local_fac.facility_name AS fac_nme
        FROM
        	dbo.tbl_facility local_fac
        FULL JOIN
        	dbo.tbl_pcc_fac pcc_fac ON pcc_fac.fac_id = local_fac.facility_id
        WHERE
        	facility_name IS NOT NULL AND pcc_fac.pcc_active = 1
        ORDER BY
        	facility_name
	'''
    # Connect to DB
    db_conn = schemaList.db_connect(db_address, fac_state)
    fac_df = pd.read_sql(fac_query, db_conn)
    # Close DB connection
    db_conn.close()
    # Merge lists and cast into dictionary
    fac_name_dict = dict(zip(list(fac_df['fac_id']), list(fac_df['fac_nme'])))
    # Format dictionary for dash output
    return_dict = [{'label':[nme+' | ID: ', id], 'value':id} for id,nme in fac_name_dict.items()]
    return return_dict, False

# Callback to generate facility graph
@main_app.callback(
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
    # Connect to DB and get all states
    db_conn = schemaList.db_connect(db_address, state)
    # Execute query to get pcc_fac_id and pcc_orguid
    tmp_pcc_fac_dataframe = pd.read_sql(fac_query, db_conn)
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
    tmp_pcc_log_dataframe = pd.read_sql(log_query, db_conn)
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
    tmp_pending_pcc_log_dataframe = pd.read_sql(pending_log_query, db_conn)
    facility_upload_log_graph.add_trace(go.Bar(x = tmp_pending_pcc_log_dataframe['cr_dte'], y = tmp_pending_pcc_log_dataframe['log_qty'], name = 'Pending'))
    # Close db connection
    db_conn.close()
    return facility_upload_log_graph, {'display': 'block'}, {'display': 'none'}

# Callback to generate global upload statistics
@main_app.callback(
    Output('global_facility_upload_log_graph', 'figure'),
    Input('update_interval', 'n_intervals')
)
def global_fac_statistics(n_intervals):
    # Connect to DB and get all states
    db_conn = schemaList.db_connect(db_address, 'Provider_App')
    query = 'SELECT st_state FROM dbo.tbl_state ORDER BY st_state;'
    query_result_df = pd.read_sql(query, db_conn)
    # Close db connection
    db_conn.close()
    tmp_st_list = ['TSC_'+state for state in query_result_df['st_state']]
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
    for state in tmp_st_list:
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, state)
        tmp_log_dataframe = pd.read_sql(query, db_conn)
        if all_sts_dataframe.empty:
            all_sts_dataframe = tmp_log_dataframe.copy()
        else:
            all_sts_dataframe = pd.concat([all_sts_dataframe, tmp_log_dataframe], ignore_index = True)
        # Close db connection
        db_conn.close()
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
    for state in tmp_st_list:
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, state)
        tmp_log_dataframe = pd.read_sql(query, db_conn)
        if all_sts_pending_dataframe.empty:
            all_sts_pending_dataframe = tmp_log_dataframe.copy()
        else:
            all_sts_pending_dataframe = pd.concat([all_sts_pending_dataframe, tmp_log_dataframe], ignore_index = True)
        # Close db connection
        db_conn.close()
    all_sts_dataframe = all_sts_dataframe.groupby('cr_dte').sum().reset_index()
    all_sts_pending_dataframe = all_sts_pending_dataframe.groupby('cr_dte').sum().reset_index()
    # Create plot
    global_fac_log_graph = make_subplots(rows = 1, cols = 1, shared_xaxes = True, shared_yaxes = True)
    # Add traces
    global_fac_log_graph.add_trace(go.Bar(x = all_sts_dataframe['cr_dte'], y = all_sts_dataframe['log_qty'], name = 'Uploaded'))
    global_fac_log_graph.add_trace(go.Bar(x = all_sts_pending_dataframe['cr_dte'], y = all_sts_pending_dataframe['log_qty'], name = 'Pending'))
    return global_fac_log_graph

# Callback to generate pending logs pie chart
@main_app.callback(
    Output('pending_logs_sunburst_chart', 'figure'),
    Input('update_interval', 'n_intervals')
)
def pending_logs_chart(n_intervals):
    # Initialize DF
    pending_logs_dataframe = pd.DataFrame()
    # Connect to DB and get all states
    db_conn = schemaList.db_connect(db_address, 'Provider_App')
    query = 'SELECT st_state FROM dbo.tbl_state ORDER BY st_state;'
    query_result_df = pd.read_sql(query, db_conn)
    # Close db connection
    db_conn.close()
    # Get db schema list
    tmp_fac_list = ['TSC_'+state for state in query_result_df['st_state']]
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
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, state)
        tmp_log_dataframe = pd.read_sql(query, db_conn)
        tmp_log_dataframe['state'] = state
        if pending_logs_dataframe.empty:
            pending_logs_dataframe = tmp_log_dataframe.copy()
        else:
            pending_logs_dataframe = pd.concat([pending_logs_dataframe, tmp_log_dataframe], ignore_index = True)
        # Close db connection
        db_conn.close()
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

if __name__ == '__main__':
    main_app.run_server(debug=True, host='0.0.0.0', port='7000', dev_tools_silence_routes_logging=False)