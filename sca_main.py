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
import sca_functions
from classes import schemaList, dbCredentials
from dash_styles import searchBarStyles, dataTableStyles, toggleInfo

db_address = dbCredentials.db_address

main_app = Dash(__name__, title='SupportiveCare Access Portal', external_stylesheets=[dbc.themes.BOOTSTRAP])
main_server = main_app.server

#---------------------------------------------LAYOUT
main_app.layout = html.Div(
    children = [
        # Works in conjunction with "active=exact" in the navlink item. Marks active items in the nav menu
        dcc.Location(id='current_url'),
        sca_functions.suppcare_header(),
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
        # App container, will be displayed based on url
        # Facility stats
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
        # Facility query
        html.Div(
            id='fac_qry_container',
            style=content.FAC_QRY_STYLE,
            children = [
                html.Div(
                    id='searchBarDiv',
                    style = searchBarStyles.searchBarFlexContainer,
                    children=[
                        dcc.Input(
                            id = 'searchBar',
                            style = searchBarStyles.searchBarFlexChildren,
                            type = 'text',
                            debounce = True,
                            placeholder = 'Ex.: Centennial Health Care'
                        ),
                        dbc.Spinner(
                            id = 'searchBarLoadingSpinner',
                            spinner_style = searchBarStyles.searchBarSpinner,
                            color = 'green',
                            show_initially = False,
                            children = []
                        )
                    ]
                ),
                html.Div(
                    dash_table.DataTable(
                        id = 'simpleSearchResultsTable',
                        style_header = dataTableStyles.style_header,
                        style_cell = dataTableStyles.style_cell,
                        style_cell_conditional = [
                            {
                                'if':{'column_id':'Name'},
                                'textAlign':'center'
                            },
                            {
                                'if':{'column_id':'State'},
                                'textAlign':'center'
                            },
                            {
                                'if':{'column_id':'Active'},
                                'textAlign':'center'
                            },
                            {
                                'if':{'column_id':'Start Date'},
                                'textAlign':'center'
                            },
                            {
                                'if':{'column_id':'PCC Request'},
                                'textAlign':'center'
                            },
                            {
                                'if':{'column_id':'Doc Types'},
                                'textAlign':'center'
                            },
                            {
                                'if':{'column_id':'Complete Data'},
                                'textAlign':'center'
                            }
                        ],
                        style_data_conditional = [
                            {
                                'if':{
                                    'column_id':'Active', 
                                    'filter_query':'{Active} = Yes'
                                },
                                'backgroundColor':'green'
                            },
                            {
                                'if':{
                                    'column_id':'Active', 
                                    'filter_query':'{Active} = No'
                                },
                                'backgroundColor':'red'
                            },
                            {
                                'if':{
                                    'column_id':'PCC Request', 
                                    'filter_query':'{PCC Request} = Yes'
                                },
                                'backgroundColor':'green'
                            },
                            {
                                'if':{
                                    'column_id':'PCC Request', 
                                    'filter_query':'{PCC Request} = No'
                                },
                                'backgroundColor':'red'
                            },
                            {
                                'if':{
                                    'column_id':'Doc Types', 
                                    'filter_query':'{Doc Types} = Yes'
                                },
                                'backgroundColor':'green'
                            },
                            {
                                'if':{
                                    'column_id':'Doc Types', 
                                    'filter_query':'{Doc Types} = No'
                                },
                                'backgroundColor':'red'
                            },
                            {
                                'if':{
                                    'column_id':'Complete Data', 
                                    'filter_query':'{Complete Data} = Complete'
                                },
                                'backgroundColor':'green'
                            }
                        ]
                    )
                ),
                dbc.Button(
                    'Technical Information',
                    id = 'technicalInfoCollapseButton',
                    color = 'primary',
                    n_clicks = 0,
                    style = toggleInfo.toggleTechnicalInfo
                ),
                dbc.Collapse(
                    dash_table.DataTable(
                        id = 'searchResultsTable',
                        style_header = dataTableStyles.style_header,
                        style_cell = dataTableStyles.style_cell,
                    ),
                    id = 'techincalInfoCollapsedDiv',
                    is_open = False
                )
            ]
        ),
        # Patient Info
        html.Div(
            id='patient_container',
            style=content.PATIENT_STYLE,
            children = [
                html.Div(
                    id='patient_search_container',
                    style=content.PATIENT_SEARCH_FLEX_STYLE,
                    children=[
                        dcc.Dropdown(
                            id = 'ptnt_state_dropdown',
                            placeholder='Select State',
                            style=content.PATIENT_STYLE_CHILD
                        ),
                        dcc.Dropdown(
                            id = 'ptnt_dropdown',
                            placeholder='Start typing patient name...',
                            disabled=True,
                            style=content.PATIENT_STYLE_CHILD
                        ),
                        dbc.Spinner(
                            id = 'ptnt_load_spinner',
                            spinner_style = searchBarStyles.searchBarSpinner,
                            color = 'green',
                            children=['Select State']
                        )
                    ]
                ),
                html.Div(
                    id='patient_result_container',
                    style=content.PATIENT_RESULT_GRID_STYLE,
                    children=[
                        dbc.Card(
                            dbc.Label('Client ID: '),
                            style=content.PATIENT_GRID_CHILD_1
                        ),
                        dbc.Card(
                            id='ptnt_id',
                            style=content.PATIENT_GRID_CHILD_7
                        ),
                        dbc.Card(
                            dbc.Label('First Name: '),
                            style=content.PATIENT_GRID_CHILD_2
                        ),
                        dbc.Card(
                            id='ptnt_first_name',
                            style=content.PATIENT_GRID_CHILD_8
                        ),
                        dbc.Card(
                            dbc.Label('Last Name: '),
                            style=content.PATIENT_GRID_CHILD_3
                        ),
                        dbc.Card(
                            id='ptnt_last_name',
                            style=content.PATIENT_GRID_CHILD_9
                        ),
                        dbc.Card(
                            dbc.Label('Facility: '),
                            style=content.PATIENT_GRID_CHILD_4
                        ),
                        dbc.Card(
                            id='ptnt_fac',
                            style=content.PATIENT_GRID_CHILD_10
                        ),
                        dbc.Card(
                            dbc.Label('Facility PCC Bridge: '),
                            style=content.PATIENT_GRID_CHILD_5
                        ),
                        dbc.Card(
                            id='ptnt_pcc_fac_bridge',
                            style=content.PATIENT_GRID_CHILD_11
                        ),
                        dbc.Card(
                            dbc.Label('Date Of Birth: '),
                            style=content.PATIENT_GRID_CHILD_6
                        ),
                        dbc.Card(
                            id='ptnt_dob',
                            style=content.PATIENT_GRID_CHILD_12
                        ),
                        dbc.Card(
                            dbc.Label('PCC Match: '),
                            style=content.PATIENT_GRID_CHILD_13
                        ),
                        dbc.Card(
                            id='ptnt_pcc_match',
                            style=content.PATIENT_GRID_CHILD_14
                        ),
                    ]
                ),
                html.Div(
                    id='ptnt_notes_container',
                    children=[
                        html.H3('Patient Notes'),
                        dash_table.DataTable(
                            id = 'ptnt_notes_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        ),
                        html.H3('Assigned Providers'),
                        dash_table.DataTable(
                            id = 'ptnt_prov_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        )
                    ]
                )
            ]
        ),
        # Provider Info
        html.Div(
            id='provider_container',
            style=content.PROV_QRY_STYLE,
            children = [
                html.Div(
                    id='prov_search_div',
                    style = searchBarStyles.searchBarFlexContainer,
                    children=[
                        dcc.Input(
                            id = 'prov_search_bar',
                            style = searchBarStyles.searchBarFlexChildren,
                            type = 'text',
                            debounce = True,
                            placeholder = 'Provider Name'
                        ),
                        dbc.Spinner(
                            id = 'prov_load_spinner',
                            spinner_style = searchBarStyles.searchBarSpinner,
                            color = 'green',
                            show_initially = False,
                            children = []
                        )
                    ]
                ),
                html.Div(
                    dash_table.DataTable(
                        id = 'prov_search_result_datatable'
                    )
                )
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
        Output('fac_qry_container', 'style'),
        Output('patient_container', 'style'),
        Output('provider_container', 'style')
    ],
    Input('current_url', 'pathname')
)
def render_container(pathname):
    # Change containers display properties depending on URL
    fac_stats_style_dic, fac_qry_style_dic, patient_style_dic, prov_qry_style_dic = sca_functions.render_container_sub(pathname)
    return fac_stats_style_dic, fac_qry_style_dic, patient_style_dic, prov_qry_style_dic

# Callback to populate the state dropdown
@main_app.callback(
    Output('state_dropdown', 'options'),
    Input('current_url', 'pathname')
    )
def populate_facility_dropdown(pathname):
    return_dict = sca_functions.populate_facility_dropdown_sub(pathname)
    if return_dict:
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
    return_dict = sca_functions.populate_fac_dropdown_sub(fac_state)
    # Return a false to enable the dropdown
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
    facility_upload_log_graph = sca_functions.generate_fac_graph_sub(local_fac_id, date_range, state)
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

# Facility Query Collapse/Expand Datatable
@main_app.callback(
    Output('techincalInfoCollapsedDiv', 'is_open'),
    Input('technicalInfoCollapseButton', 'n_clicks'),
    State('techincalInfoCollapsedDiv', 'is_open')
)
def showTechnicalInfo(n, is_open):
    if n:
        return not is_open
    return is_open

# Facility Query Results
@main_app.callback(
    [
        Output('searchResultsTable', 'columns'),
        Output('searchResultsTable', 'data'),
        Output('simpleSearchResultsTable', 'columns'),
        Output('simpleSearchResultsTable', 'data'),
        Output('searchBarLoadingSpinner', 'children')
    ],
    [
        Input('searchBar', 'value')
    ]
    )
def searchQueryResult(facName):
    tmp_fac_dict = schemaList.schemaDict
    pccFactTblDataframe = pd.DataFrame()
    simplePccFactTblDataframe = pd.DataFrame(columns = ['Name', 'State', 'Active', 'Start Date', 'PCC Request', 'Doc Types', 'Complete Data'])
    fac_query = '''SELECT 
    	facility.facility_id, 
    	facility.facility_name, 
    	facility.facility_street, 
    	facility.facility_city, 
    	facility.facility_state,
    	sessiondata.First_session,
    	pccFacility.st_dte,
    	pccFacility.pcc_orgUid,
    	pccFacility.pcc_facID,
    	pccFacility.pcc_active,
    	pccFacility.pickListID,
    	pccFacility.aimsDocID,
    	pccFacility.phqDocID,
    	pccFacility.bimsDocID,
    	pccFacility.psychDocID,
    	pccFacility.evalDocID,
    	pccFacility.progDocID,
    	pccFacility.pcc_docs
    FROM
    	dbo.tbl_facility facility
    FULL JOIN 
    	dbo.vw_ys_fac_first_ses_dte sessiondata ON facility.facility_id = sessiondata.facility_id
    FULL JOIN
    	dbo.tbl_pcc_fac pccFacility ON facility.facility_id = pccFacility.fac_id
    WHERE
    	facility.facility_name LIKE '%{}%';
    '''.format(facName)
    for schema,payload in tmp_fac_dict.items():
        # Instantiate engine class
        engineInstance = sqlalchemy.create_engine('mssql+pyodbc://sqlsvr:61433/{}?trusted_connection=yes&driver=SQL Server Native Client 11.0'.format(schema))
        #engine_instance = sqlalchemy.create_engine('mssql+pyodbc://sqlsvr:61433/{}?trusted_connection=yes&driver=ODBC Driver 17 for SQL Server'.format(schema))
        # Establish connection
        try:
            connectionInstance = engineInstance.connect()
            #logging.info('Connected to {}'.format(schema))
            tmpDataframe = pd.read_sql(fac_query, connectionInstance)
            # Fill missing data with 0 or blank
            tmpDataframe['aimsDocID'] = tmpDataframe['aimsDocID'].fillna(0)
            tmpDataframe['phqDocID'] = tmpDataframe['phqDocID'].fillna(0)
            tmpDataframe['bimsDocID'] = tmpDataframe['bimsDocID'].fillna(0)
            tmpDataframe['psychDocID'] = tmpDataframe['psychDocID'].fillna(0)
            tmpDataframe['evalDocID'] = tmpDataframe['evalDocID'].fillna(0)
            tmpDataframe['progDocID'] = tmpDataframe['progDocID'].fillna(0)
            tmpDataframe['pcc_orgUid'] = tmpDataframe['pcc_orgUid'].fillna("")
            # If dataframe is empty, then create columns and fill with the data from the first schema
            if pccFactTblDataframe.empty:
                pccFactTblDataframe = tmpDataframe.copy()
            else:
                # Append the temporal DF to the pccFactTblDataframe
                pccFactTblDataframe = pd.concat([pccFactTblDataframe, tmpDataframe], ignore_index=True)
            # Loop through tmpDataframe and append data to tmpList
            for i in range(len(tmpDataframe['facility_name'])):
                tmpList = []
                tmpList.append(tmpDataframe['facility_name'][i])
                # Append current schema's state
                tmpList.append(payload[3])
                # Append "Yes" if facility is active on db
                tmpList.append('Yes') if tmpDataframe['pcc_active'][i] == 1 else tmpList.append('No')
                tmpList.append(tmpDataframe['st_dte'][i])
                # Check if pcc_orgUid exists
                tmpList.append('Yes') if len(tmpDataframe['pcc_orgUid'][i]) > 0 else tmpList.append('No')
                # Check if Doc Types are in
                tmpList.append('Yes') if tmpDataframe['aimsDocID'][i]+tmpDataframe['phqDocID'][i]+tmpDataframe['bimsDocID'][i]+tmpDataframe['psychDocID'][i]+tmpDataframe['evalDocID'][i]+tmpDataframe['progDocID'][i] > 0 else tmpList.append('No')
                # Check if there's any data missing to enable the button
                if tmpDataframe['aimsDocID'][i] != 0 and tmpDataframe['phqDocID'][i] != 0 and tmpDataframe['bimsDocID'][i] != 0 and tmpDataframe['psychDocID'][i] != 0 and tmpDataframe['evalDocID'][i] != 0 and tmpDataframe['progDocID'][i] != 0 and len(tmpDataframe['pcc_orgUid'][i]) > 0 and tmpDataframe['pcc_active'][i] == 1:
                    tmpList.append('Complete')
                else:
                    tmpList.append('Missing')
                simplePccFactTblDataframe.loc[len(simplePccFactTblDataframe['Name'])] = tmpList
        except SQLAlchemyError as errorMessage:
            #logging.debug(errorMessage)
            pass
        try:
            # Must close connection prior to dropping the table, to avoid simultaneous connections
            connectionInstance.close()
            #logging.info('Closing connection to {}'.format(schema))
        except:
            pass
    columnsReturnValue = [{'name':i, 'id':i} for i in pccFactTblDataframe.columns]
    simpleColumnsReturnValue = [{'name':i, 'id':i} for i in simplePccFactTblDataframe.columns]
    return columnsReturnValue, pccFactTblDataframe.to_dict('records'), simpleColumnsReturnValue, simplePccFactTblDataframe.to_dict('records'), 'Ready to Search'

# Query provider's info
@main_app.callback(
    [
        Output('prov_search_result_datatable', 'columns'),
        Output('prov_search_result_datatable', 'data'),
        Output('prov_load_spinner', 'children')
    ],
    Input('prov_search_bar', 'value')
)
def search_provider(prov_nme):
    # Connect to DB and get all states
    db_conn = schemaList.db_connect(dbCredentials.db_address, 'Provider_App')
    query = 'SELECT st_state,back_office_email_address FROM dbo.tbl_state ORDER BY st_state;'
    query_result_df = pd.read_sql(query, db_conn)
    # Cast 2 column df into dictionary
    query_result_dict = pd.Series(query_result_df['back_office_email_address'].values, index=query_result_df['st_state']).to_dict()
    # Close db connection
    db_conn.close()
    provider_info_dataframe = pd.DataFrame()
    query = '''SELECT     
			localprov.ProviderID, 
			localprov.ProviderName, 
			localprov.ProviderEmail, 
			hub_user.PhoneNumber,
			hub_user.UserName AS HubUsername,
			localprov.prov_inactive AS ProviderInactive,
			provtype.provider_type AS ProviderLicense,
			servicetype.svce_type AS ProviderType
		FROM            
			dbo.ProviderTable localprov
		FULL JOIN
			dbo.tbl_provider_type provtype ON localprov.provider_type = provtype.provider_type_id
		FULL JOIN
			dbo.tbl_svce_type servicetype ON provtype.svce_type_id = servicetype.svce_type_id
		FULL JOIN
			Provider_App.dbo.AspNetUsers hub_user ON hub_user.Email = localprov.ProviderEmail
		WHERE        
			(ProviderName LIKE '%{}%');
    	'''.format(prov_nme)
    for state,referral_inbox in query_result_dict.items():
        db_conn = schemaList.db_connect(dbCredentials.db_address, "TSC_"+state)
        # Execute query
        tmp_dataframe = pd.read_sql(query, db_conn)
        tmp_dataframe['State'] = state
        tmp_dataframe['Referral'] = referral_inbox
        # If final DF is empty, then copy tmp to final
        if provider_info_dataframe.empty:
            provider_info_dataframe['State'] = ""
            provider_info_dataframe['Referral'] = ""
            provider_info_dataframe = tmp_dataframe.copy()
        else:
            # Append the temporal DF to the final DF
        	provider_info_dataframe = pd.concat([provider_info_dataframe, tmp_dataframe], ignore_index=True)
        # Close connetion
        schemaList.db_close(db_conn)
    columnsReturnValue = [{'name':i, 'id':i} for i in provider_info_dataframe.columns]
    return columnsReturnValue, provider_info_dataframe.to_dict('records'), 'Ready to Search'

# Poplate patient state list
@main_app.callback(
    Output('ptnt_state_dropdown', 'options'),
    Input('current_url', 'pathname')
    )
def populate_ptnt_st_dropdown(pathname):
    if pathname == '/patients_info':
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, 'Provider_App')
        query = 'SELECT st_id,st_state FROM dbo.tbl_state ORDER BY st_state;'
        query_result_df = pd.read_sql(query, db_conn)
        query_result_dict = dict(zip(list(query_result_df['st_id']), list(query_result_df['st_state'])))
        # Give format for dash dropdowns
        return_dict = [{'label':[state+' | State ID: ',id], 'value': 'TSC_'+state} for id,state in query_result_dict.items()]
        # Close db connection
        db_conn.close()
        return return_dict
    else:
        raise PreventUpdate

# Poplate patient list
@main_app.callback(
    [
        Output('ptnt_dropdown', 'options'),
        Output('ptnt_dropdown', 'disabled'),
        Output('ptnt_load_spinner', 'children')
    ],
    Input('ptnt_state_dropdown', 'value'),
    prevent_initial_call=True
    )
def populate_ptnt_dropdown(state):
    ptnt_info_df = pd.DataFrame()
    # Get all patient's list
    db_conn = schemaList.db_connect(dbCredentials.db_address, state)
    query = '''
        SELECT
        	ClientID,
        	CONCAT(LastName, ', ', FirstName) AS ClientName,
            CASE WHEN Status = 187 THEN 'Active' ELSE 'Inactive' END AS Status
        FROM            
        	dbo.ClientInfoTable
        ORDER BY ClientName;
    '''
    tmp_df=pd.read_sql(query, db_conn)
    # If dataframe is empty, then create columns and fill with the data from the first schema
    if ptnt_info_df.empty:
        ptnt_info_df = tmp_df.copy()
    else:
        # Append the temporal DF to the ptnt_info_df
        ptnt_info_df = pd.concat([ptnt_info_df, tmp_df], ignore_index=True)
    # Close DB connection
    schemaList.db_close(db_conn)
    # Close db connection
    db_conn.close()
    # Give format for dash dropdowns
    return_dict = [{'label':[ptnt_info_df['ClientName'][i]+' | ClientID: '+str(ptnt_info_df['ClientID'][i])+' | Status: '+ptnt_info_df['Status'][i]], 'value': ptnt_info_df['ClientID'][i]} for i in range(len(ptnt_info_df['ClientID']))]
    return return_dict, False, 'Select Patient'

# Query patient's info
@main_app.callback(
        [
            Output('ptnt_first_name', 'children'),
            Output('ptnt_last_name', 'children'),
            Output('ptnt_id', 'children'),
            Output('ptnt_dob', 'children'),
            Output('ptnt_fac', 'children'),
            Output('ptnt_pcc_match', 'children'),
            Output('ptnt_pcc_fac_bridge', 'children'),
            Output('ptnt_notes_table', 'columns'),
            Output('ptnt_notes_table', 'data'),
            Output('ptnt_prov_table', 'columns'),
            Output('ptnt_prov_table', 'data')
        ],
    Input('ptnt_dropdown', 'value'),
    State('ptnt_state_dropdown', 'value'),
    prevent_initial_call=True
)
def query_ptnt_info(ptnt_id, state):
    # Connect to State DB
    db_conn = schemaList.db_connect(dbCredentials.db_address, state)
    query = '''
        SELECT        
        	clientinfo.ClientID AS ClientID, 
        	clientinfo.LastName AS LastName, 
        	clientinfo.FirstName AS FirstName, 
        	FORMAT(clientinfo.DateOfBirth, 'yyyy-MM-dd') AS DateOfBirth, 
        	localfac.facility_name AS facility_name,
            pccfac.fac_id AS pcc_fac_id,
        	pccclientinfo.pcc_id AS matched
        FROM            
        	dbo.ClientInfoTable clientinfo
        INNER JOIN
        	dbo.tbl_facility localfac ON clientinfo.facility_id = localfac.facility_id
        FULL OUTER JOIN
            dbo.tbl_pcc_fac pccfac ON clientinfo.facility_id = pccfac.fac_id
        FULL OUTER JOIN
        	dbo.tbl_pcc_patients_client pccclientinfo ON clientinfo.ClientID = pccclientinfo.cl_id
        WHERE
        	ClientID = {}
    '''.format(ptnt_id)
    ptnt_info_df=pd.read_sql(query, db_conn)
    # Query patient's providers
    query  = '''
        SELECT
        	prov_table.ProviderName,
        	prov_table.ProviderEmail, 
        	FORMAT(prov_roster.roster_st_date, 'yyyy-MM-dd') AS 'Start Date',
        	FORMAT(prov_roster.roster_end_date, 'yyyy-MM-dd') AS 'End Date',
        	prov_roster.roster_not_covered, 
        	service_type.svce_type
        FROM
        	dbo.tbl_roster prov_roster
        INNER JOIN
        	dbo.ProviderTable prov_table ON prov_table.ProviderID = prov_roster.prov_id
        INNER JOIN
        	dbo.tbl_svce_type service_type ON service_type.svce_type_id = prov_roster.svce_type_id
        WHERE
        	prov_roster.cl_id = {}
        ORDER BY prov_table.ProviderName, prov_roster.roster_st_date;
    '''.format(ptnt_id)
    ptnt_prov_df = pd.read_sql(query, db_conn)
    # Close DB connection
    schemaList.db_close(db_conn)
    # Connect to Provider_App DB
    db_conn = schemaList.db_connect(dbCredentials.db_address, 'Provider_App')
    # Get state ID
    query = '''SELECT st_id FROM dbo.tbl_state WHERE st_state = '{}';'''.format(state[-2:])
    state_id = pd.read_sql(query, db_conn)['st_id'][0]
    # Query patient's notes
    query = '''
        SELECT
        	notes_log.note_id AS 'Note ID', 
        	notes_log.note_tbl_name AS 'State Table', 
            notes_log.prov_nme AS Provider, 
        	notes_log.svce_type AS 'Service Type', 
        	notes_log.note_type AS 'Note Type', 
        	notes_log.cpt_code AS 'CPT Code', 
        	FORMAT(notes_log.note_dte, 'yyyy-MM-dd')  AS 'Service Date', 
        	notes_log.note_del AS 'Delete Flag', 
        	FORMAT(notes_log.create_dte, 'yyyy-MM-dd hh:mm') AS 'Create Date', 
        	FORMAT(notes_log.mod_dte, 'yyyy-MM-dd hh:mm') AS 'Modify Date', 
        	FORMAT(notes_log.prov_sig_dte, 'yyyy-MM-dd hh:mm') AS 'Signature Date', 
        	FORMAT(pcc_log.cr_dte, 'yyyy-MM-dd hh:mm') AS 'Log Create Date',
        	FORMAT(pcc_log.done_dte, 'yyyy-MM-dd hh:mm') AS 'Log Done Date'
        FROM
        	Provider_App.dbo.tbl_notes_log notes_log
        FULL JOIN
        	{}.dbo.tbl_pcc_upl_log pcc_log ON pcc_log.uniqueID = notes_log.note_id
        WHERE
        	notes_log.cl_id = {} AND notes_log.note_dte >= (GETDATE() - 90) AND notes_log.st_id = {}
        ORDER BY notes_log.note_dte DESC
    '''.format(state, ptnt_id, state_id)
    ptnt_notes_df = pd.read_sql(query, db_conn)
    # Format patient's notes df for dash datatable
    ptnt_notes_columns = [{'name':i, 'id':i} for i in ptnt_notes_df.columns]
    ptnt_notes_data = ptnt_notes_df.to_dict('records')
    # Close DB connection
    schemaList.db_close(db_conn)
    return ptnt_info_df['FirstName'][0], ptnt_info_df['LastName'][0], ptnt_info_df['ClientID'][0], ptnt_info_df['DateOfBirth'][0], ptnt_info_df['facility_name'][0], 'PCC ID '+str(ptnt_info_df['matched'][0]) if ptnt_info_df['matched'][0] != None else 'No', ptnt_info_df['pcc_fac_id'], ptnt_notes_columns, ptnt_notes_data, [{'name':i, 'id':i} for i in ptnt_prov_df.columns], ptnt_prov_df.to_dict('records')

if __name__ == '__main__':
    main_app.run_server(debug=True, host='0.0.0.0', port='7000', dev_tools_silence_routes_logging=False)