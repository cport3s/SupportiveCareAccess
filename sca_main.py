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
from dash_styles import nav_bar
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
        dbc.Nav(
            [
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
            id='sca_main_container',
            style=nav_bar.CONTENT_STYLE,
            children = [
                suppcare_header(),
                html.H2(
                    children = ['Facility Statistics'],
                    style = SuppCareBanner.orange_style
                ),
                html.Div(
                    id = 'facility_dropdown_container',
                    children = [
                        dcc.Dropdown(
                            id = 'state_dropdown',
                            #options = [{'label': v[-2], 'value': k} for k,v in schemaList.schemaDict.items()],
                            #value = 'All'
                        ),
                        dcc.Dropdown(
                            id = 'facility_dropdown'
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
                ),
                dcc.Interval(
                    id = 'update_interval',
                    interval = 3000*1000,
                    n_intervals = 0
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
    Output('sca_main_container', 'style'),
    Input('current_url', 'pathname')
)
def render_container(pathname):
    # sca_main_container div content will be updated based on URL
    layout_return = html.P('filler')
    if pathname == '/fac_stats':
        return {'display': 'inline'}
    else:
        return {'display': 'hidden'}

# Callback to populate the state dropdown
@main_app.callback(
    Output('state_dropdown', 'options'),
    Input('current_url', 'pathname'),
    prevent_initial_call=True
    )
def populate_facility_dropdown(pathname):
    if pathname == '/fac_stats':
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, 'Provider_App')
        query = 'SELECT st_state FROM dbo.tbl_state ORDER BY st_state;'
        query_result_df = pd.read_sql(query, db_conn)
        return_dict = [{'label':state, 'value':state} for state in query_result_df['st_state']]
        return return_dict
    else:
        raise PreventUpdate

if __name__ == '__main__':
    main_app.run_server(debug=True, host='0.0.0.0', port='7000', dev_tools_silence_routes_logging=False)