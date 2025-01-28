# delete_umbrella (hidden API)

This script deletes the Umbrella configuration for a specific SSID in all networks (or a specified network) in an organization

# Quick Start

1. Clone Repository. 
2. Login to meraki dashboard with an account that has privileges to modify SSID settings for desired SSID you wish to remove Umbrella integration
3. When logged in, browse to desired organization with developer tools open (CMD+Opt+I on mac)
4. On the Network tab, refresh the page and find the `administered_orgs` call, right-click and copy the URL, this is the `administered-orgs-url` argument
5. Right-click again and select copy value > Copy as cURL
6. Go to curlconverter.com and paste in the contents
7. The Cookies variable listed should have the dictionary enclosed in single quotes, this is your `--cookies` argument
8. The headers variable listed should have the dictionary enclosed in single quotes, this is your `--headers` argument
9. Scroll to the bottom of whatever dashboard page you are on, copy the numbers in the `(organization ID: )` parenthesis, this is your `--org-id` variable
10. Optionally enter a network name for the `--network-name` argument

** Example Command (will not work) **

```
python delete_umbrella_ssid.py -n "totally_valid_network_name" -o internal_org_id -a https://n999.meraki.com/o/unique_id/manage/organization/administered_orgs --headers '{"User-Agent": "some_browser","Accept": "application/json, text/javascript, */*; q=0.01","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate, br, zstd","X-CSRF-Token": "good_csrf_token ","X-Pageload-Request-Id": "invalid_id","X-Requested-With": "XMLHttpRequest","Connection": "keep-alive","Referer": "some_url_here","Sec-Fetch-Dest": "empty","Sec-Fetch-Mode": "cors","Sec-Fetch-Site": "same-origin"}' --cookies '{"dash_auth": "invalid-dash-auth","_session_id_for_n999": "invalid",}'
```
Your headers and cookies will vary.