import os
import requests
import pandas as pd

BaseUrl = ""
OpsRampSecret = ''  # Replace with your OpsRamp Secret
OpsRampKey = ''  

def get_auth_headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

def token():
    try:
        token_url = BaseUrl + "auth/oauth/token"
        auth_data = {
            'client_secret': OpsRampSecret,
            'grant_type': 'client_credentials',
            'client_id': OpsRampKey
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_response = requests.post(token_url, data=auth_data, headers=headers, verify=True)
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            return token_data.get('access_token')
        else:
            print("Failed to obtain access token:", token_response.text)
            return None
    except Exception as e:
        print("An error occurred during token generation:", str(e))
        return None

def agentcheck(access_token, client_uid, device_uid):
    try:
        if access_token is None:
            print("Access token is not available")
            return None, None, None, None, None

        auth_header = get_auth_headers(access_token)
        manage_resources_url = BaseUrl + f"api/v2/tenants/{client_uid}/resources/{device_uid}"
        response = requests.get(manage_resources_url, headers=auth_header, verify=True)
        
        if response.status_code == 200:
            resources_data = response.json()
            agent_status = resources_data.get('agentStatus')
            management_profile_data = resources_data.get('managementProfile')
            profile_name = management_profile_data.get('name') if management_profile_data else "No profile"

            # Extract tags
            tags = resources_data.get('tags', [])
            sku_device_scope = None
            service_device_scope = None

            for tag in tags:
                if tag.get('name') == "SKU Device - Partner Scope":
                    sku_device_scope = tag.get('value')
                elif tag.get('name') == "Service Device - Partner Scope":
                    service_device_scope = tag.get('value')

            return agent_status, profile_name, sku_device_scope, service_device_scope
        else:
            print("Failed to retrieve agent info:", response.text)
            return None, None, None, None, None
    except Exception as e:
        print("An error occurred:", str(e))
        return None, None, None, None, None

def main():
    # Load client and device IDs from Excel
    input_data = pd.read_excel('input_devices.xlsx')
    
    access_token = token()
    results = []

    for index, row in input_data.iterrows():
        client_uid = row['client_uid']
        device_uid = row['device_uid']
        partner_name = row['partner_name']
        client_name = row['client_name']
        
        agent_status, profile_name, sku_device_scope, service_device_scope = agentcheck(access_token, client_uid, device_uid)
        
        results.append({
            'Client UID': client_uid,
            'Device UID': device_uid,
            'Partner Name': partner_name,
            'Client Name': client_name,
            'Agent Status': agent_status,
            'Management Profile': profile_name,
            'SKU Device - Partner Scope': sku_device_scope,
            'Service Device - Partner Scope': service_device_scope
        })

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(results)
    df.to_excel('agent_check_results.xlsx', index=False)

if __name__ == "__main__":
    main()
