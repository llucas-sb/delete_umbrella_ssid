import argparse
import meraki_dashboard
from copy import deepcopy

def arguments ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--ssid-number', required=True,
                        action='store', nargs='?', default=0,
                        type=int, help='Integer of the SSID number for which you want to remove Umbrella configuration.')
    parser.add_argument('-u', '--username', default='',
                        type=str, help='email for dashboard login (should be non-sso account).')
    parser.add_argument('-p', '--password', default='',
                        type=str, help='Password for provided login email address.')
    parser.add_argument('-o', '--org-id', default='',
                        type=str, help='Organization number shown at the bottom of the meraki dashboard when looking at any element of a single org.')
    parser.add_argument('-on', '--org-name', default='',
                        type=str, help='Name of organization for which you want umbrella removed from the specified ssid in all networks.')
    parser.add_argument('-n', '--network-name', default=[], nargs='+',
                        help="Network Name(s) for which you want umbrella removed from the ssid.")

    return parser.parse_args()

def purge_umbrella(dashboard: type[meraki_dashboard.MerakiDashboardAPI], locale: type[meraki_dashboard.locales], ssid_number: int):
   if "wireless" in locale._fields:
        print("DELETING UMBRELLA CONFIGURATION FOR NETWORK: ", locale.name)
        #### FORMAT PAYLOAD
        data = {
            'entityType': 'ssid',
            'entityNumber': ssid_number
        }
        headers = deepcopy(dashboard._json_headers)
        headers['Accept'] = 'application/json, text/javascript, */*, q=0.01'
        headers['Referer'] = dashboard._last_uri
        headers['X-CSRF-TOKEN'] = dashboard.shard_headers[locale.shard_id]['csrf_token']
        headers['X-Pageload-Request-Id'] = dashboard.shard_headers[locale.shard_id]['pageload_id']
        headers['X-Requested-With'] = 'XMLHttpRequest'
        #### FORMAT URL
        url = 'https://n{locale.shard_id}.meraki.com/{locale.tag}/n/{locale.wireless}/manage/configure/disconnect_umbrella'.format(locale=locale)
        print("URL: ", url)
        #### SEND REQUEST
        response = dashboard.session.post(
            url,
            headers=headers,
            data=data,
        )
        #### PRINT RESPONSE
        if response.status_code == 200:
            print("SUCCESSFULLY DELETED UMBRELLA CONFIGURATION FOR NETWORK: ", locale.name, "\n\n")
        else:
            print("FAILED TO DELETE UMBRELLA CONFIGURATION FOR NETWORK: ", locale.name)
            print("STATUS CODE: ", response.status_code)
            print("RESPONSE TEXT: ", response.text)
            print("RESPONSE JSON: ", response.json(), "\n\n")

def main (username: str, password: str, org_id: str, org_name: str, network_name: list, ssid_number: int):

    dashboard = meraki_dashboard.MerakiDashboardAPI(username=username, password=password)
    
    dashboard.meraki_login()
    locale_list = []
    if (org_id or org_name) != '':
        # unfortunate reality of multi-org accounts is we don't know what orgs we can access (specifically their shard_ids)
        # until we make at least one call to get administered_orgs, we'll call the default, check if we have our desired org
        # if not we will make a second call and ideally we have it then, or a typo
        dashboard.get_org_data(id=org_id, name=org_name)
        dashboard.parse_values()
        desired_org = dashboard.get_org(name=org_name, id=org_id)
        if desired_org.id == '':
            dashboard.get_org_data(id=org_id, name=org_name)
            desired_org = dashboard.get_org(name=org_name, id=org_id)
        if desired_org.id != '':
            locale_list.extend([locale for locale in dashboard.locales if locale.org_id == desired_org.id])
    else:
        #### GET ALL ORGS AND NETWORKS
        print("GETTING ORGANIZATIONS AND NETWORK DATA...")
        dashboard.get_orgs_data()
        dashboard.parse_values()
    if len(network_name) > 0:
        locale_list.extend([locale for locale in dashboard.locales if locale.name in network_name])
    if len(locale_list) > 0:
        # user a set() to remove duplicate locales
        for i,locale in enumerate(set(locale_list)):
            purge_umbrella(dashboard, locale, ssid_number)
            if i % 100 == 0:
                dashboard.refresh_token(locale.shard_id)
    else:
        print("No networks selected/found in dashboard data.")

if __name__ == "__main__":
    main_args = arguments()
    main(username=main_args.username,
         password=main_args.password,
         org_id=main_args.org_id,
         org_name=main_args.org_name,
         network_name=main_args.network_name,
         ssid_number=main_args.ssid_number,
         )
