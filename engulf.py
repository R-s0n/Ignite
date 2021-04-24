# Automated Parameter Discovery

import requests, sys, subprocess, getopt, json, time, math, random
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "u:"
long_options = ["url="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

hasUrl = False

for current_argument, current_value in arguments:
    if current_argument in ("-u", "--url"):
        url = current_value
        hasUrl = True

if hasUrl == False:
    print("[!] Please enter a URL using the -d or --domain flag...")
    sys.exit(2)

start = time.time()

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

now_start = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Engulf.py - Start Time: {now_start}\n")
f.close()

r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
thisUrl = r.json()

try:
    endpoints = thisUrl['endpoints']
    sorted_endpoints = sorted(endpoints, key=lambda k: k['statusCode'])
except:
    print(f"[!] URL '{url}' was not found in the database.  Exiting...")
    sys.exit(2)

for endpoint in sorted_endpoints:
    if str(endpoint['statusCode'])[0] == '2':
        print(f"Endpoint: {endpoint['endpoint']}\nStatus: {endpoint['statusCode']} -- Length: {endpoint['responseLength']}")
        try:
            if endpoint['endpoint'][0] == "/":
                thisEndpoint = endpoint['endpoint'][1:]
            else:
                thisEndpoint = endpoint['endpoint']
            if thisEndpoint[-4:] == ".ico" or thisEndpoint[-4:] == ".txt":
                print(f"[!] Endpoint is a static file.  Skipping...")
                continue
        except:
            print("[-] Targeting root directory...")
            thisEndpoint = ""
        target = url + thisEndpoint
        print(f"[-] Scanning {target} for hidden parameters...")
        subprocess.run([f"arjun -u {target} -oJ /tmp/arjun-test.tmp -w /home/rs0n/Wordlists/SecLists/Discovery/Web-Content/params.txt"], shell=True)
        with open('/tmp/arjun-test.tmp') as json_file:
            data = json.load(json_file)
        print(f"[+] Scan complete!")
        print(f"[-] Updating database...")
        r = requests.post('http://10.0.0.211:8000/api/url/auto', data={'url':url})
        updateUrl = r.json()
        for endpoint in updateUrl['endpoints']:
            if endpoint['endpoint'] == thisEndpoint:
                endpointToUpdate = endpoint
                endpointIndex = updateUrl['endpoints'].index(endpoint)
        print(f"Updating {endpointToUpdate} at index {endpointIndex}...")
        updateUrl['endpoints'][endpointIndex]['arjun'] = {"method": data[target]['method'], "params": data[target]['params']}
        print(updateUrl['endpoints'][endpointIndex])
        requests.post('http://10.0.0.211:8000/api/url/auto/update', json=updateUrl)