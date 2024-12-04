from dash import html, dcc
from dash_styles import SuppCareBanner
from classes import schemaList

# Header code function, to avoid code repetion
def suppcare_header():
    header = html.A(
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
                    href='http://localhost:7000/',
                    style = SuppCareBanner.a_element_style
                )
    return header

def run_all_schemas():
    pass