import json
import requests
import argparse

def arguments ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--ssid-number',
                        action='store', nargs='?', default=0,
                        type=int, help='Integer of the SSID number for which you want to remove Umbrella configuration.')
    parser.add_argument('-o', '--org-id', required=True,
                        type=str, help='Organization number shown at the bottom of the meraki dashboard when looking at any element of a single org.')
    parser.add_argument('-a', '--administered-orgs-url', required=True,
                        type=str, help='Entire URL of the dashboard API call /manage/organization/administered_orgs, can be any you are authorized to look at')
    parser.add_argument('--headers', required=True,
                        type=str, help='json output of headers used for the administered_orgs call in string format')
    parser.add_argument('--cookies', required=True,
                        type=str, help='json output of cookies used for an authenticated call on the dashboard in string format')
    parser.add_argument('-n', '--network-name', default='',
                        type=str, help="(Optional) network name of singular network to target for umbrella removal")

    return parser.parse_args()

def purge_umbrella(org_json_data: dict, org_id: str,
                    network: str, ssid_number: int,
                    headers: dict, cookies: dict):
    
    network_id = org_json_data[org_id]['locales'][network]['id']
    #### GET ALL NETWORKS WITH TYPE "WIRELESS"
    if "wireless" in org_json_data[org_id]['locales'][network]:
        net = org_json_data[org_id]['locales'][network_id]
        network_name = net['name']
        network_short_name = net['tag']
        network_id = network,
        ui_wireless_id = net['wireless']
        shard_id = org_json_data[org_id]['shard_id']

        print("DELETING UMBRELLA CONFIGURATION FOR NETWORK: ", network_name)

        #### FORMAT PAYLOAD
        data = {
            'entityType': 'ssid',
            'entityNumber': ssid_number
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

def main (user_headers: str, ssid_number: int, org_id: str,
            administered_orgs_url: str, target_network_name: str,
            user_cookies: str):

    cookies = json.loads(user_cookies)

    headers = json.loads(user_headers)

    #### GET ALL ORGS AND NETWORKS
    print("GETTING ORGANIZATIONS...")

    administered_orgs = requests.get(
        administered_orgs_url,
        cookies=cookies,
        headers=headers,
    )

    #### SINCE ONLY THE ACTIVE ORG RETURNS NETWORK DATA, WE NEED TO LOOP THROUGH ALL ORGS TO FIND THE ONE WE WANT
    for administered_org in administered_orgs.json():
        if administered_org == org_id:
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
            org_json_data = org.json()

            #### PARSE NETWORKS
            for network in org_json_data[org_id]['locales']:
                if target_network_name:
                    if target_network_name == org_json_data[org_id]['locales'][network]['name']:
                        purge_umbrella(org_json_data, org_id, network, ssid_number, headers, cookies)
                else:
                    purge_umbrella(org_json_data, org_id, network, ssid_number, headers, cookies)



if __name__ == "__main__":
    main_args = arguments()
    main(user_headers=main_args.headers,
            user_cookies=main_args.cookies,
            ssid_number=main_args.ssid_number,
            org_id=main_args.org_id,
            administered_orgs_url=main_args.administered_orgs_url,
            target_network_name=main_args.network_name)
