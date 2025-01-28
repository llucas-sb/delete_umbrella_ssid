##########################################################################################################
# Description: This script deletes the Umbrella configuration for a specific SSID in all networks
# in an organization
# 
# Requirements:
# - Python 3
# - Requests library
#
# Instructions:
# 1. Enter the organization ID in the 'ORG_ID' variable.
# 2. Enter the SSID number you want to delete the Umbrella configuration for in the 'SSID_NUMBER' variable.
# 3. Update ADMINISTERED_ORGS_URL with the URL of the Meraki Dashboard for your organization.
# 4. Replace the Cookies and Headers in the script with the ones from your browser.
# 5. Run the script.
# 6. The script will output the results of the operation.
#
# Note: This script is provided as is without warranty or liability. Use at your own risk.
# Cisco Meraki support will not be able to provide support for this script.
#
# An HTTP 400 error will be returned for any networks that do not have the Umbrella integration
# enabled at the network level.
#
# This script was written by Nathan Wiens.
#
##########################################################################################################

import json
import requests

#### CHANGE THIS TO THE SSID NUMBER YOU WANT TO DELETE UMBRELLA CONFIGURATION FOR
ORG_ID = '692200'
SSID_NUMBER = 2
ADMINISTERED_ORGS_URL = 'https://n276.meraki.com/o/QZcwfa/manage/organization/administered_orgs'


#### COPY THESE FROM AN AUTHENTICATED BROWSER SESSION. CONVERT FROM cURL to PYTHON AT CURLCONVERTER.COM
cookies = {}

headers = {}

#### GET ALL ORGS AND NETWORKS
print("GETTING ORGANIZATIONS...")

administered_orgs = requests.get(
    ADMINISTERED_ORGS_URL,
    cookies=cookies,
    headers=headers,
)

#### SINCE ONLY THE ACTIVE ORG RETURNS NETWORK DATA, WE NEED TO LOOP THROUGH ALL ORGS TO FIND THE ONE WE WANT
for administered_org in administered_orgs.json():
    if administered_org == ORG_ID:
        #### ONCE WE'VE FOUND THE ORG, WE CAN GET THE NETWORKS
        org_name = administered_orgs.json()[administered_org]['name']
        org_eid = administered_orgs.json()[administered_org]['eid']
        org_shard_id = administered_orgs.json()[administered_org]['shard_id']

        url = f'https://n{org_shard_id}.meraki.com/o/{org_eid}/manage/organization/administered_orgs'

        org = requests.get(
            url,
            cookies=cookies,
            headers=headers,
        )

        #### PARSE NETWORKS
        for network in org.json()[ORG_ID]['locales']:
            network_id = org.json()[ORG_ID]['locales'][network]['id']
            #### GET ALL NETWORKS WITH TYPE "WIRELESS"
            if "wireless" in org.json()[ORG_ID]['locales'][network]:
                net = org.json()[ORG_ID]['locales'][network_id]
                network_name = net['name']
                network_short_name = net['tag']
                network_id = network,
                ui_wireless_id = net['wireless']
                shard_id = org.json()[ORG_ID]['shard_id']

                print("DELETING UMBRELLA CONFIGURATION FOR NETWORK: ", network_name)

                #### FORMAT PAYLOAD
                data = {
                    'entityType': 'ssid',
                    'entityNumber': SSID_NUMBER
                }

                #### FORMAT URL
                url = f'https://n{shard_id}.meraki.com/{network_short_name}/n/{ui_wireless_id}/manage/configure/disconnect_umbrella'
                print("URL: ", url)

                #### SEND REQUEST
                response = requests.post(
                    url,
                    cookies=cookies,
                    headers=headers,
                    data=data,
                )

                #### PRINT RESPONSE
                if response.status_code == 200:
                    print("SUCCESSFULLY DELETED UMBRELLA CONFIGURATION FOR NETWORK: ", network_name, "\n\n")
                else:
                    print("FAILED TO DELETE UMBRELLA CONFIGURATION FOR NETWORK: ", network_name)
                    print("STATUS CODE: ", response.status_code)
                    print("RESPONSE TEXT: ", response.text)
                    print("RESPONSE JSON: ", response.json(), "\n\n")
