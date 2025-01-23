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

def populate_fac_info_dropdown(pathname):
    if pathname == '/fac_info':
        # Create an empty dataframe to store all data
        pcc_fac_dataframe = pd.DataFrame()
        # Connect to DB and get all states
        db_conn = schemaList.db_connect(db_address, 'Provider_App')
        query = 'SELECT st_state FROM dbo.tbl_state ORDER BY st_state;'
        query_result_df = pd.read_sql(query, db_conn)
        # Close db connection
        db_conn.close()
        # Loop through all states and get all facilities
        for state in query_result_df['st_state']:
            # Connect to each state's DB
            db_conn = schemaList.db_connect(db_address, state)
            query = '''
                SELECT
                	facility_id, 
                	facility_name,
                    db_name() AS state
                FROM            
                	dbo.tbl_facility
            '''
            # Check if dataframe is empty
            if pcc_fac_dataframe.empty:
                pcc_fac_dataframe = pd.read_sql(query, db_conn)
            else:
                pcc_fac_dataframe = pd.concat([pcc_fac_dataframe, pd.read_sql(query, db_conn)], ignore_index=True)
            # Close db connection
            db_conn.close()
        # Sort dataframe by facility name
        pcc_fac_dataframe = pcc_fac_dataframe.sort_values(by='facility_name', ignore_index=True)
        # Give format for dash dropdowns
        return_dict = [{'label':[pcc_fac_dataframe['facility_name'][i]+' | State: '+pcc_fac_dataframe['state'][i]], 'value': str(pcc_fac_dataframe['facility_id'][i])+'|'+pcc_fac_dataframe['state'][i]} for i in range(len(pcc_fac_dataframe['facility_id']))]
        return return_dict
    else:
        return False
    
def query_fac_info_sub(fac_dropdown_value):
    state = fac_dropdown_value.split('|')[1].strip()
    fac_id = fac_dropdown_value.split('|')[0].strip()
    # Connect to DB
    db_conn = schemaList.db_connect(db_address, state)
    # Query facility's PCC bridge status
    query = '''
        SELECT 
        	facility.facility_id AS 'Local ID', 
	        facility.facility_street AS Street, 
	        facility.facility_city AS City, 
	        FORMAT(sessiondata.First_session, 'yyyy-MM-dd') AS 'First Session Date',
	        FORMAT(pccFacility.st_dte, 'yyyy-MM-dd') AS 'PCC Start Date',
	        pccFacility.pcc_orgUid AS 'Org ID',
	        pccFacility.pcc_facID AS 'PCC ID',
	        pccFacility.pcc_active AS 'PCC Active',
            pccFacility.pickListID,
	        CONCAT(CAST(pccFacility.aimsDocID AS VARCHAR(4)), '|', CAST(pccFacility.phqDocID AS VARCHAR(4)), '|', CAST(pccFacility.bimsDocID AS VARCHAR(4)), '|', CAST(pccFacility.psychDocID AS VARCHAR(4)), '|', CAST(pccFacility.evalDocID AS VARCHAR(4)), '|', CAST(pccFacility.progDocID AS VARCHAR(4))) AS 'DocID'
        FROM
        	dbo.tbl_facility facility
        FULL JOIN 
        	dbo.vw_ys_fac_first_ses_dte sessiondata ON facility.facility_id = sessiondata.facility_id
        FULL JOIN
        	dbo.tbl_pcc_fac pccFacility ON facility.facility_id = pccFacility.fac_id
        WHERE
        	facility.facility_id = {};
    '''.format(fac_id)
    # Execute query
    pcc_status_df = pd.read_sql(query, db_conn)
    # Get all facility notes
    query = '''
        SELECT       
        	prov_fac.prov_id AS 'Provider ID', 
        	provider.ProviderName AS 'Provider Name',
        	provider.ProviderEmail AS 'Email',
        	prov_type.provider_type AS 'License',
        	service_type.svce_type AS 'Service Type',
            CASE WHEN provider.prov_inactive = 1 THEN 'Inactive' ELSE 'Active' END AS Status
        FROM            
        	dbo.tbl_provider_fac prov_fac
        INNER JOIN
        	dbo.tbl_svce_type service_type ON service_type.svce_type_id = prov_fac.svce_id
        FULL OUTER JOIN
        	dbo.ProviderTable provider ON provider.ProviderID = prov_fac.prov_id
        FULL OUTER JOIN
        	dbo.tbl_provider_type prov_type ON prov_type.provider_type_id = provider.provider_type
        WHERE
        	prov_fac.facility_id = {}
        ORDER BY service_type.svce_type, provider.ProviderName;
    '''.format(fac_id)
    # Execute query
    pcc_prov_df = pd.read_sql(query, db_conn)
    # Close db connection
    db_conn.close()
    # Connect to DB
    db_conn = schemaList.db_connect(db_address, 'Provider_App')
    # Get all facility notes
    query = '''
        SELECT 
            note_log.cl_id AS 'Client ID',
        	note_log.cl_nme AS 'Patient Name',
            note_log.prov_nme AS 'Provider',
            FORMAT(note_log.note_dte, 'yyyy-MM-dd') AS 'Session Date',
        	note_log.svce_type AS 'Service Type', 
        	note_log.note_type AS 'Session Type', 
        	note_log.cpt_code AS 'CPT Code', 
        	note_log.note_id AS 'Session ID',
        	FORMAT(upl_log.cr_dte, 'yyyy-MM-dd hh:mm') AS 'Upload Entry',
        	FORMAT(upl_log.done_dte, 'yyyy-MM-dd hh:mm') AS 'Upload Date'
        FROM            
        	dbo.tbl_notes_log note_log
        INNER JOIN 
        	dbo.tbl_state statetable ON statetable.st_id = note_log.st_id
        FULL OUTER JOIN
        	{}.dbo.tbl_pcc_upl_log upl_log ON upl_log.uniqueID = note_log.note_id
        WHERE        
        	note_log.fac_id = {} AND statetable.st_state = '{}' AND note_log.note_dte >= (GETDATE() - 30)
        ORDER BY note_dte DESC;
    '''.format(state, fac_id, state[-2:])
    # Execute query
    pcc_notes_df = pd.read_sql(query, db_conn)
    # Close db connection
    db_conn.close()
    return pcc_status_df, pcc_prov_df, pcc_notes_df

def global_fac_statistics_sub():
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

def pending_logs_chart_sub():
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

