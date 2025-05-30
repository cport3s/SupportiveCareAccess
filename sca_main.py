from dash import Dash, html, dcc, dash_table, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
from dash_styles import nav_bar, content
import sca_functions
from classes import schemaList, dbCredentials
from dash_styles import searchBarStyles

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
                dbc.NavLink('Patient Matching', href='/patient_match', active='exact'),
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
                        dcc.Dropdown(
                            id='fac_dropdown',
                            style = searchBarStyles.searchBarFlexChildren,
                            placeholder='Start typing facility name...'
                        ),
                        dbc.Spinner(
                            id = 'searchBarLoadingSpinner',
                            spinner_style = searchBarStyles.searchBarSpinner,
                            color = 'green',
                            show_initially = False,
                            children = ['Select Facility']
                        )
                    ]
                ),
                html.Div(
                    id='fac_search_result_container',
                    children=[
                        html.H3('PCC Bridge Status'),
                        dash_table.DataTable(
                            id = 'fac_pcc_status_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        ),
                        html.H3('Notes'),
                        dash_table.DataTable(
                            id = 'fac_notes_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=5,
                            filter_action='native'
                        ),
                        html.H3('Providers'),
                        dash_table.DataTable(
                            id = 'fac_prov_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=5,
                            filter_action='native'
                        )
                    ]
                )
            ]
        ),
        # Patient Match
        html.Div(
            id='patient_match_container',
            style=content.PATIENT_MATCH_STYLE,
            children = [
                dcc.Input(
                    id='ptnt_last_name_input',
                    type='text',
                    placeholder='Type Patient\'s Last Name',
                ),
                dcc.Input(
                    id='ptnt_first_name_input',
                    type='text',
                    placeholder='Type Patient\'s First Name',
                ),
                html.H3('PCC Client Table'),
                dash_table.DataTable(
                    id='ptnt_match_result_table',
                    style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                    },
                    page_size=5,
                    filter_action='native'
                ),
                html.H3('Local Client Table'),
                dash_table.DataTable(
                    id='local_client_match_result_table',
                    style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                    },
                    page_size=5,
                    filter_action='native'
                ),
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
                            },
                            page_size=10,
                            filter_action='native'
                        ),
                        html.H3('Assigned Providers'),
                        dash_table.DataTable(
                            id = 'ptnt_prov_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=10,
                            filter_action='native'
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
                        dcc.Dropdown(
                            id = 'prov_dropdown',
                            style = searchBarStyles.searchBarFlexChildren,
                            placeholder = 'Provider Name'
                        )
                    ]
                ),
                html.Div(
                    id='prov_search_result_container',
                    children=[
                        html.H3('Provider Info'),
                        dash_table.DataTable(
                            id = 'prov_info_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            }
                        ),
                        html.H3('Facilities'),
                        dash_table.DataTable(
                            id = 'prov_fac_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=10,
                            filter_action='native'
                        ),
                        html.H3('Notes'),
                        dash_table.DataTable(
                            id = 'prov_notes_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=10,
                            filter_action='native'
                        ),
                        html.H3('Patients'),
                        dash_table.DataTable(
                            id = 'prov_ptnt_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=10,
                            filter_action='native'
                        ),
                        html.H3('Paystub'),
                        dash_table.DataTable(
                            id = 'prov_paystub_table',
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto'
                            },
                            page_size=10,
                            filter_action='native'
                        )
                    ]
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
        Output('patient_match_container', 'style'),
        Output('provider_container', 'style')
    ],
    Input('current_url', 'pathname')
)
def render_container(pathname):
    # Change containers display properties depending on URL
    fac_stats_style_dic, fac_qry_style_dic, patient_style_dic, fac_map_style_dic, prov_qry_style_dic = sca_functions.render_container_sub(pathname)
    return fac_stats_style_dic, fac_qry_style_dic, patient_style_dic, fac_map_style_dic, prov_qry_style_dic

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
    global_fac_log_graph = sca_functions.global_fac_statistics_sub()
    return global_fac_log_graph

# Callback to generate pending logs sunburst chart
@main_app.callback(
    Output('pending_logs_sunburst_chart', 'figure'),
    Input('update_interval', 'n_intervals')
)
def pending_logs_chart(n_intervals):
    pending_logs_pie = sca_functions.pending_logs_chart_sub()
    return pending_logs_pie

# Populate Facility Dropdown
@main_app.callback(
    Output('fac_dropdown', 'options'),
    Input('current_url', 'pathname')
)
def populate_fac_dropdown(pathname):
    fac_info_dict = sca_functions.populate_fac_info_dropdown(pathname)
    if fac_info_dict:
        return fac_info_dict
    else:
        raise PreventUpdate

# Facility Query Results
@main_app.callback(
        [
            Output('fac_pcc_status_table', 'columns'),
            Output('fac_pcc_status_table', 'data'),
            Output('fac_prov_table', 'columns'),
            Output('fac_prov_table', 'data'),
            Output('fac_notes_table', 'columns'),
            Output('fac_notes_table', 'data')
        ],
        Input('fac_dropdown', 'value'),
        prevent_initial_call=True
)
def query_fac_info(fac_dropdown_value):
    if fac_dropdown_value:
        pcc_status_df, pcc_prov_df, pcc_notes_df = sca_functions.query_fac_info_sub(fac_dropdown_value)
        return [{'name':i, 'id':i} for i in pcc_status_df.columns], pcc_status_df.to_dict('records'), [{'name':i, 'id':i} for i in pcc_prov_df.columns], pcc_prov_df.to_dict('records'), [{'name':i, 'id':i} for i in pcc_notes_df.columns], pcc_notes_df.to_dict('records')
    else:
        raise PreventUpdate

# Callback to populate provider dropdown
@main_app.callback(
    Output('prov_dropdown', 'options'),
    Input('current_url', 'pathname')
    )
def populate_prov_dropdown(pathname):
    if pathname == '/prov_info':
        return_dict = sca_functions.populate_prov_dropdown_sub(pathname)
        return return_dict
    else:
        raise PreventUpdate

# Query provider's info
@main_app.callback(
    [
        Output('prov_info_table', 'columns'),
        Output('prov_info_table', 'data'),
        Output('prov_fac_table', 'columns'),
        Output('prov_fac_table', 'data'),
        Output('prov_ptnt_table', 'columns'),
        Output('prov_ptnt_table', 'data'),
        Output('prov_notes_table', 'columns'),
        Output('prov_notes_table', 'data'),
        Output('prov_paystub_table', 'columns'),
        Output('prov_paystub_table', 'data')
    ],
    Input('prov_dropdown', 'value'),
    prevent_initial_call=True
)
def query_prov_info(prov_info):
    prov_info_df, prov_fac_df, prov_ptnt_df, prov_notes_df, prov_paystub_df = sca_functions.query_prov_info_sub(prov_info)
    return [{'name':i, 'id':i} for i in prov_info_df.columns], prov_info_df.to_dict('records'), [{'name':i, 'id':i} for i in prov_fac_df.columns], prov_fac_df.to_dict('records'), [{'name':i, 'id':i} for i in prov_ptnt_df.columns], prov_ptnt_df.to_dict('records'), [{'name':i, 'id':i} for i in prov_notes_df.columns], prov_notes_df.to_dict('records'), [{'name':i, 'id':i} for i in prov_paystub_df.columns], prov_paystub_df.to_dict('records')

# Poplate patient state list
@main_app.callback(
    Output('ptnt_state_dropdown', 'options'),
    Input('current_url', 'pathname')
    )
def populate_ptnt_st_dropdown(pathname):
    if pathname == '/patients_info':
        return_dict = sca_functions.populate_ptnt_st_dropdown_sub()
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
    return_dict = sca_functions.populate_ptnt_dropdown_sub(state)
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
    db_conn.close()
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
        	notes_log.cl_id = {} AND notes_log.st_id = {}
        ORDER BY notes_log.note_dte DESC
    '''.format(state, ptnt_id, state_id)
    ptnt_notes_df = pd.read_sql(query, db_conn)
    # Format patient's notes df for dash datatable
    ptnt_notes_columns = [{'name':i, 'id':i} for i in ptnt_notes_df.columns]
    ptnt_notes_data = ptnt_notes_df.to_dict('records')
    # Close DB connection
    db_conn.close()
    return ptnt_info_df['FirstName'][0], ptnt_info_df['LastName'][0], ptnt_info_df['ClientID'][0], ptnt_info_df['DateOfBirth'][0], ptnt_info_df['facility_name'][0], 'PCC ID '+str(ptnt_info_df['matched'][0]) if ptnt_info_df['matched'][0] != None else 'No', ptnt_info_df['pcc_fac_id'], ptnt_notes_columns, ptnt_notes_data, [{'name':i, 'id':i} for i in ptnt_prov_df.columns], ptnt_prov_df.to_dict('records')

# Callback to query facilities address and generate map
@main_app.callback(
    [
        Output('ptnt_match_result_table', 'columns'),
        Output('ptnt_match_result_table', 'data'),
        Output('local_client_match_result_table', 'columns'),
        Output('local_client_match_result_table', 'data')
    ],
    [
        Input('current_url', 'pathname'),
        Input('ptnt_last_name_input', 'value'),
        Input('ptnt_first_name_input', 'value')
    ]
)
def generate_fac_map(pathname, last_name, first_name):
    if pathname == '/patient_match':
        ptnt_match_df, local_client_match_df = sca_functions.ptnt_match_query(last_name, first_name)
        return [{'name':i, 'id':i} for i in ptnt_match_df.columns], ptnt_match_df.to_dict('records'), [{'name':i, 'id':i} for i in local_client_match_df.columns], local_client_match_df.to_dict('records')
    else:
        raise PreventUpdate

if __name__ == '__main__':
    main_app.run_server(debug=True, host='0.0.0.0', port='7000', dev_tools_silence_routes_logging=False)