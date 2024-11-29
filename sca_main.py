from dash import Dash, html, dcc, dash_table, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from dash_styles import nav_bar
from sca_functions import get_layout

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
            style=nav_bar.CONTENT_STYLE
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
    Output('sca_main_container', 'children'),
    Input('current_url', 'pathname')
)
def render_container(pathname):
    # sca_main_container div content will be updated based on URL
    layout_return = get_layout(pathname)
    return layout_return

if __name__ == '__main__':
    main_app.run_server(debug=True, host='0.0.0.0', port='7000', dev_tools_silence_routes_logging=False)