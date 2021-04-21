import requests, sys, subprocess, getopt, json, time, math, random
from datetime import datetime

full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
short_options = "d:"
long_options = ["domain="]

try:
    arguments, values = getopt.getopt(argument_list, short_options, long_options)
except:
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in ("-d", "--domain"):
        fqdn = current_value

start = time.time()

get_home_dir = subprocess.run(["echo $HOME"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
home_dir = get_home_dir.stdout.replace("\n", "")

now_start = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Ignite.py - Start Time: {now_start}\n")
f.close()

r = requests.post('http://10.0.0.211:8000/api/url/all', data={})
urls = r.json()

url_list = []

for u in urls:
    if u['fqdn'] == fqdn:
        if u['url'][-1:] == "/":
            url_list.append(u['url'][:-1])
        else:
            url_list.append(u['url'])

print(url_list)

wordlists = subprocess.run([f"ls {home_dir}/Wordlists/SecLists/Discovery/Web-Content/"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
wordlist_arr = wordlists.stdout.split('\n')
wordlist_arr.pop()
dir_arr = []

for wordlist in wordlist_arr:
    if wordlist[-4:] != ".txt":
        dir_arr.append(wordlist)
        i = wordlist_arr.index(wordlist)
        del wordlist_arr[i]

for directory in dir_arr:
    dir_str = subprocess.run([f"ls {home_dir}/Wordlists/SecLists/Discovery/Web-Content/{directory}"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
    dir_arr_temp = dir_str.stdout.split('\n')
    dir_arr_temp.pop()
    for sub_wordlist in dir_arr_temp:
        if sub_wordlist[-4:] == ".txt":
            wordlist_arr.append(f"{directory}/{sub_wordlist}")

for target_url in url_list:
    l = len(wordlist_arr)-1
    for x in range(l):
        wordlist = random.choice(wordlist_arr)
        format_test = subprocess.run([f"head -n 1 {home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist}"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, shell=True)
        print(format_test.stdout[0])
        if format_test.stdout[0] == "/":
            subprocess.run([f'{home_dir}/go/bin/ffuf -w {home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist} -u {target_url}FUZZ -recursion -recursion-depth 2 -r -p 0.1-3.0 -sa -t 50 -replay-proxy http://10.0.0.208:8080'], shell=True)
        else:
            subprocess.run([f'{home_dir}/go/bin/ffuf -w {home_dir}/Wordlists/SecLists/Discovery/Web-Content/{wordlist} -u {target_url}/FUZZ -recursion -recursion-depth 2 -r -p 0.1-3.0 -sa -t 50 -replay-proxy http://10.0.0.208:8080'], shell=True)
        i = wordlist_arr.index(wordlist)
        del wordlist_arr[i]

now_end = datetime.now().strftime("%d-%m-%y_%I%p")
f = open(f"{home_dir}/Logs/automation.log", "a")
f.write(f"Ignite.py - End Time: {now_end}\n")
f.close()

end = time.time()
runtime_seconds = math.floor(end - start)
runtime_minutes = math.floor(runtime_seconds / 60)

print(f"[+] Ignite.py completed successfully in {runtime_minutes} minutes!")