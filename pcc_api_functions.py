import requests
import json
from datetime import datetime
import pandas as pd
import json

def get_pcc_access_token(connection):
    # If there's no connection token, then connect and generate a new one
    if(connection.check_auth_token() == False):
        encoded_auth64 = connection.encode_auth_code()
        # Set headers (as per PCC documentation)
        headers_dict = {
            'content-type': 'application/x-www-form-urlencoded', 
            # Authorization key must be sent encoded
            'authorization': 'Basic ' + str(encoded_auth64)
        }
        # Set payload (as per PCC documentation)
        data_dict = {
            'grant_type': 'client_credentials'
        }
        # Get access token
        connection.access_token = requests.post(connection.access_token_url, data=data_dict, headers=headers_dict).json()
        # Get current datetime
        current_auth_token_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        json_dict = {'token_date': current_auth_token_datetime, 'access_token': connection.access_token['access_token'], 'expires_in': connection.access_token['expires_in']}
        # Write access token values to json file
        with open('pcc_access_token.json', 'w') as json_file:
            json.dump(json_dict, json_file)

def request_pcc_activation_requests(connection):
    # Function connects to PCC API and retrieves activation requests
    access_tokn = connection.access_token['access_token']
    # Setup header
    headers_dict = { 
        'content-type': 'application/json', 
        # authorization key must be sent encoded
        'authorization': 'Bearer ' + access_tokn
    }
    # Make API call
    pcc_fac_req = requests.get(connection.pcc_api_url, headers=headers_dict).json()
    # Initialize empty dataframe to store pcc_fac_req data, organized
    pcc_fac_req_df = pd.DataFrame(columns = ['facId', 'orgUuid', 'activationDate', 'scope'])
    # Loop through the "Data" key (whose value is a list)
    for data_row in pcc_fac_req['data']:
        # Create temporary dictionary to add row at the end of pcc_fac_req_df
        tmp_dataframe = {'facId':'', 'orgUuid':'', 'activationDate':'', 'scope':''}
        tmp_dataframe['orgUuid'] = data_row['orgUuid']
        tmp_dataframe['scope'] = data_row['scope']
        # facilityInfo does not exists if pcc request is for deactivation
        if 'facilityInfo' in data_row:
            for facility in data_row['facilityInfo']:
                tmp_dataframe['facId'] = facility['facId']
                tmp_dataframe['activationDate'] = facility['activationDate']
                # Append tmp_dataframe to final df
                pcc_fac_req_df.loc[len(pcc_fac_req_df)] = tmp_dataframe
        else:
            tmp_dataframe['facId'] = 'N/A'
            tmp_dataframe['activationDate'] = 'N/A'
            # Append tmp_dataframe to final df
            pcc_fac_req_df.loc[len(pcc_fac_req_df)] = tmp_dataframe
    pcc_fac_req_df.to_excel('./pcc_act_req/activation_requests_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.xlsx')
    return pcc_fac_req_df

def check_orguid_facility(activation_df, connection):
    # Setup header
    headers_dict = { 
        'content-type': 'application/json', 
        # authorization key must be sent encoded
        'authorization': 'Bearer ' + connection.access_token['access_token']
    }
    # Make API call
    api_url_call = 'https://connect.pointclickcare.com/api/public/preview1/orgs/{}/facs'
    # Save file into WebAccess's folder
    csv_file_name = 'C:\\Code\\SupportiveCareAccess\\pcc_activations\\pcc_activations_{}.csv'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
    with open(csv_file_name, 'a') as csv_file:
        # Write header to CSV file
        csv_file.write("orgUuid, facId, facilityName, active, healthType\n")
        for orguid in activation_df['orgUuid'].unique():
            # Make API call
            pcc_fac_req = requests.get(api_url_call.format(orguid), headers=headers_dict).json()
            if 'data' in pcc_fac_req.keys():
                for facility in pcc_fac_req['data']:
                    facility['facilityName'] = facility['facilityName'].replace(',', '')
                    facility['orgName'] = facility['orgName'].replace(',', '')
                    #print("Org UUID: {}, Facility ID: {}, Facility Name: {}".format(facility['orgUuid'], facility['facId'], facility['facilityName']))
                    # Write all into a CSV file
                    csv_file.write("{}, {}, {}, {}, {}\n".format(facility['facilityName'], facility['orgUuid'], facility['facId'], facility['orgName'], facility['state'], facility['healthType']))
            # Check token validity
            if pcc_fac_req.status_code != 200:
                get_pcc_access_token(connection)

def request_pcc_patients(activation_df, connection):
    # Setup header
    headers_dict = { 
        'content-type': 'application/json', 
        # authorization key must be sent encoded
        'authorization': 'Bearer ' + connection.access_token['access_token']
    }
    # Make API call
    api_url_call = 'https://connect.pointclickcare.com/api/public/preview1/orgs/{}/patients?facId={}&page={}&pageSize=100'
    bad_request_df = pd.DataFrame(columns=['timestamp', 'orgUuid', 'facId', 'error'])
    patient_df = pd.DataFrame(columns=['patientId', 'facId', 'orgUuid', 'patientStatus', 'firstName', 'lastName', 'birthDate', 'dischargeDate'])
    # First, loop through each OrgUUID
    for i in range(len(activation_df['orgUuid'])):
        page = 1
        while page > 0:
            # Check token validity
            if connection.check_auth_token() == False:
                get_pcc_access_token(connection)
            # Call the API with OrgUUID, FacID and page number
            pcc_ptnt_req = requests.get(api_url_call.format(activation_df['orgUuid'][i], activation_df['facId'][i], page), headers=headers_dict)
            if pcc_ptnt_req.status_code != 200:
                print("Error: {}, OrgUUID: {}, FacID: {}".format(pcc_ptnt_req.status_code, activation_df['orgUuid'][i], activation_df['facId'][i]))
                # Store bad requests information into dataframe
                bad_request_df.loc[len(bad_request_df)] = {
                    'timestamp': datetime.now(),
                    'orgUuid': activation_df['orgUuid'][i],
                    'facId': activation_df['facId'][i],
                    'error': pcc_ptnt_req.status_code
                }
                break
            else:
                pcc_ptnt_req = pcc_ptnt_req.json()
                print(pcc_ptnt_req)
                if 'data' in pcc_ptnt_req.keys():
                    for patient in pcc_ptnt_req['data']:
                        # Fill in case value is missing
                        patient['birthDate'] = '' if 'birthDate' not in patient else patient['birthDate']
                        patient['dischargeDate'] = '' if 'dischargeDate' not in patient else patient['dischargeDate']
                        patient['firstName'] = '' if 'firstName' not in patient else patient['firstName']
                        patient['lastName'] = '' if 'lastName' not in patient else patient['lastName']
                        patient['patientStatus'] = '' if 'patientStatus' not in patient else patient['patientStatus']
                        # Append patient data to patient_df
                        patient_df.loc[len(patient_df)] = {
                            'patientId': patient['patientId'],
                            'firstName': patient['firstName'],
                            'lastName': patient['lastName'],
                            'birthDate': patient['birthDate'],
                            'facId': activation_df['facId'][i],
                            'orgUuid': activation_df['orgUuid'][i],
                            'patientStatus': patient['patientStatus'],
                            'dischargeDate': patient['dischargeDate']
                        }
                # Check the paging value
                if 'paging' in pcc_ptnt_req.keys():
                    # If there are more pages, then increment page value
                    if pcc_ptnt_req['paging']['hasMore'] is True:
                        page += 1
                    else:
                        page = 0
    # Save file into WebAccess's folder
    csv_file_name = 'C:\\Code\\SupportiveCareAccess\\pcc_patients\\pcc_patients_{}_{}.csv'.format(ptnt_status, datetime.now().strftime('%Y%m%d%H%M%S'))
    bad_request_file_name = 'C:\\Code\\SupportiveCareAccess\\pcc_patients\\pcc_bad_requests_{}.csv'.format(datetime.now().strftime('%Y%m%d%H%M%S'))
    # Write patient_df to CSV file
    patient_df.to_csv(csv_file_name, index=False)
    # Write bad_request_df to CSV file
    if not bad_request_df.empty:
        bad_request_df.to_csv(bad_request_file_name, index=False)
    return patient_df, bad_request_df

def get_picklist_id(orguuid, facid, connection):
    # Setup header
    headers_dict = { 
        'content-type': 'application/json', 
        # authorization key must be sent encoded
        'authorization': 'Bearer ' + connection.access_token['access_token']
    }
    # Make API call
    api_url_call = 'https://connect.pointclickcare.com/api/public/preview1/orgs/{}/pick-lists?facId={}'
    # Save file into WebAccess's folder
    csv_file_name = 'C:\\Code\\SupportiveCareAccess\\pcc_pick_list\\pick_list_org_{}_fac_{}_{}.csv'.format(orguuid, facid, datetime.now().strftime('%Y%m%d%H%M%S'))
    with open(csv_file_name, 'a') as csv_file:
        # Write header to CSV file
        csv_file.write("orgUuid, facId, Category ID, name, description\n")
        page = 1
        while page > 0:
            # Check token validity
            if connection.check_auth_token() == False:
                get_pcc_access_token(connection)
            # Make API call
            doc_id_req = requests.get(api_url_call.format(orguuid, facid), headers=headers_dict)
            if doc_id_req.status_code != 200:
                get_pcc_access_token(connection)
                break
            else:
                doc_id_req = doc_id_req.json()
                if 'data' in doc_id_req.keys():
                    for category in doc_id_req['data']:
                        print("Org UUID: {}, Facility ID: {}, Category ID: {}, Category Name: {}, Category Description: {}".format(category['orgUuid'], category['facId'], category['pickListId'], category['name'], category['description']))
                        # Write all into a CSV file
                        csv_file.write("{}, {}, {}, {}, {}\n".format(category['orgUuid'], category['facId'], category['pickListId'], category['name'], category['description']))
            # Check the paging value
            if 'paging' in doc_id_req.keys():
                # If there are more pages, then increment page value
                if doc_id_req['paging']['hasMore'] is True:
                    page += 1
                else:
                    page = 0

def get_doc_id(orguuid, facid, connection):
    # Setup header
    headers_dict = { 
        'content-type': 'application/json', 
        # authorization key must be sent encoded
        'authorization': 'Bearer ' + connection.access_token['access_token']
    }
    # Make API call
    api_url_call = 'https://connect.pointclickcare.com/api/public/preview1/orgs/{}/pick-lists/27?facId={}'
    # Save file into WebAccess's folder
    csv_file_name = 'C:\\Code\\SupportiveCareAccess\\pcc_doc_id\\doc_category_org_{}_fac_{}_{}.csv'.format(orguuid, facid, datetime.now().strftime('%Y%m%d%H%M%S'))
    with open(csv_file_name, 'a') as csv_file:
        # Write header to CSV file
        csv_file.write("orgUuid, facId, Category ID, description\n")
        page = 1
        while page > 0:
            # Check token validity
            if connection.check_auth_token() == False:
                get_pcc_access_token(connection)
            # Make API call
            doc_id_req = requests.get(api_url_call.format(orguuid, facid), headers=headers_dict)
            if doc_id_req.status_code != 200:
                get_pcc_access_token(connection)
                break
            else:
                doc_id_req = doc_id_req.json()
                if 'elements' in doc_id_req.keys():
                    for category in doc_id_req['elements']:
                        print("Org UUID: {}, Facility ID: {}, Category ID: {}, Category Description: {}".format(orguuid, facid, category['id'], category['description']))
                        # Write all into a CSV file
                        csv_file.write("{}, {}, {}, {}\n".format(orguuid, facid, category['id'], category['description']))
            # Check the paging value
            if 'paging' in doc_id_req.keys():
                # If there are more pages, then increment page value
                if doc_id_req['paging']['hasMore'] is True:
                    page += 1
                else:
                    page = 0