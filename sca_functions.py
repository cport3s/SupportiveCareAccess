from dash import html, dcc
from dash_styles import SuppCareBanner
from classes import schemaList

def get_layout(pathname):
    layout_return = html.P('filler')
    if pathname == '/fac_stats':
        layout_return = html.Div(
            children = [
                html.A(
                    children = [
                        html.H1(
                            children = [
                                html.Span(
                                    children = ['Support'],
                                    style = SuppCareBanner.blue_style,
                                ),
                                html.Span(
                                    children = ['i'],
                                    style = SuppCareBanner.green_style,
                                ),
                                html.Span(
                                    children = ['ve '],
                                    style = SuppCareBanner.blue_style,
                                ),
                                html.Span(
                                    children = ['Care'],
                                    style = SuppCareBanner.green_style,
                                )
                            ],
                            style = SuppCareBanner.banner_style
                        )
                    ],
                    #href='http://websvr:8000/',
                    style = SuppCareBanner.a_element_style
                ),
                html.H2(
                    children = ['Facility Statistics'],
                    style = SuppCareBanner.orange_style
                ),
                html.Div(
                    id = 'facility_dropdown_container',
                    children = [
                        dcc.Dropdown(
                            id = 'state_dropdown',
                            options = [{'label': v[-2], 'value': k} for k,v in schemaList.schemaDict.items()],
                            value = 'All'
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
        )
    return layout_return