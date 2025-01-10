from dash import html, dcc
from dash_styles import SuppCareBanner
from classes import schemaList, dbCredentials
from dash_styles import nav_bar, content
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

db_address = dbCredentials.db_address

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

# Switch between containers depending on URL
def render_container_sub(pathname):
    # Change containers display properties depending on URL
    fac_stats_style_dic = content.FAC_STATS_STYLE
    patient_style_dic = content.PATIENT_STYLE
    fac_qry_style_dic = content.FAC_QRY_STYLE
    prov_qry_style_dic = content.PROV_QRY_STYLE
    if pathname == '/fac_stats':
        fac_stats_style_dic['display']='block'
        patient_style_dic['display']='none'
        fac_qry_style_dic['display']='none'
        prov_qry_style_dic['display']='none'
    elif pathname == '/patients_info':
        fac_stats_style_dic['display']='none'
        patient_style_dic['display']='block'
        fac_qry_style_dic['display']='none'
        prov_qry_style_dic['display']='none'
    elif pathname == '/fac_info':
        fac_stats_style_dic['display']='none'
        patient_style_dic['display']='none'
        fac_qry_style_dic['display']='block'
        prov_qry_style_dic['display']='none'
    elif pathname == '/prov_info':
        fac_stats_style_dic['display']='none'
        patient_style_dic['display']='none'
        fac_qry_style_dic['display']='none'
        prov_qry_style_dic['display']='block'
    else:
        fac_stats_style_dic['display']='none'
        patient_style_dic['display']='none'
        fac_qry_style_dic['display']='none'
        prov_qry_style_dic['display']='none'
    return fac_stats_style_dic, fac_qry_style_dic, patient_style_dic, prov_qry_style_dic

# Populate state dropdown in facility stats page
def populate_facility_dropdown_sub(pathname):
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
        return False
    
# Populate facility dropdown in facility stats page
def populate_fac_dropdown_sub(fac_state):
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
    return return_dict

def generate_fac_graph_sub(local_fac_id, date_range, state):
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
    return facility_upload_log_graph