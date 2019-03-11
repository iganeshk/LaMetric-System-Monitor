#!/usr/bin/env/ python3
# coding=utf-8
#
# Parse OpenHardwareMonitor's Remote Data (JSON) and publish it to LaMetric
# Ganesh Velu

import time
import requests
import json
# import yaml

# load up secrets file to get config
# with open("secrets.yaml") as secrets_file:
#     secrets = yaml.safe_load(secrets_file)

OPENHARDWAREMONITOR_URL = "YOUR_COMPUTER_IP:8085/data.json"
TIMEOUT = 1
LA_TOKEN = "YOUR_APP_TOKEN"
LA_PUSH_URL_LOCAL = "YOUR_LOCAL_PUSH_URL"
HEADERS = {'Accept': 'application/json', 'X-Access-Token': LA_TOKEN, "Cache-Control": "no-cache"}

# Temperature thresholds for dynamic Icons
ICON_THRESHOLD_TEMP_HOT = "70"
ICON_THRESHOLD_TEMP_COLD = "45"


def push_hwinfo(json_data):
    # disable warning about the certificate for local push
    requests.packages.urllib3.disable_warnings()
    response = requests.post(LA_PUSH_URL_LOCAL, data=json.dumps(json_data), headers=HEADERS, verify=False)


def parse_ohm():
    # get the data from open hardware monitor (make sure port 8085 is open on windows firewall)
    try:
        json_data = requests.get(OPENHARDWAREMONITOR_URL, verify=False, timeout=5).json()

        # parse data to get cpu package temperature (this key is for package value)
        cpu_vcore = json_data['Children'][0]['Children'][0]['Children'][0]['Children'][0]['Children'][0]['Value'][:4]

        # parse data to get cpu package temperature (this key is for package value)
        cpu_temp = json_data['Children'][0]['Children'][1]['Children'][1]['Children'][6]['Value'][:2]

        # parse data to get gpu package temperature (this key is for package value)
        gpu_temp = json_data['Children'][0]['Children'][3]['Children'][1]['Children'][0]['Value'][:2]

        # change icon between hot and cold based on the threshold set
        if(cpu_temp < ICON_THRESHOLD_TEMP_COLD):
            cpu_icon = "a26356"
        elif(cpu_temp >= ICON_THRESHOLD_TEMP_COLD and cpu_temp <= ICON_THRESHOLD_TEMP_HOT):
            cpu_icon = "a26358"
        else:
            cpu_icon = "a26357"
        if(gpu_temp < ICON_THRESHOLD_TEMP_COLD):
            gpu_icon = "a26356"
        elif(gpu_temp >= ICON_THRESHOLD_TEMP_COLD and gpu_temp <= ICON_THRESHOLD_TEMP_HOT):
            gpu_icon = "a26358"
        else:
            gpu_icon = "a26357"
        json_data = {"frames": [{"text": "CPU " + cpu_temp + "°", "icon": cpu_icon},
                                {"text": "GPU " + gpu_temp + "°", "icon": gpu_icon},
                                {"text": "VC " + cpu_vcore, "icon": "a27512"}]}
        push_hwinfo(json_data)
        # catch timeouts and report offline to Time
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
        json_data = {"frames": [{"text": "SYSTEM OFFLINE", "icon": "a27513"}]}
        # json_data = {"frames": [{"text": "SYSTEM OFFLINE", "icon": "a22294"}]}
        push_hwinfo(json_data)
    # exit if unable to reach Time
    except (ValueError, IndexError):
        print("Unable to fetch CPU/GPU Temperature, check the json to fix the keys.")
    except requests.exceptions.ConnectionError:
        print("Unable to reach LaMetric Time, check your connection")
    # exit(1)


if __name__ == '__main__':
    try:
        while True:
            timed_start = time.time()
            parse_ohm()
            # print("tick")
            time.sleep(TIMEOUT)
    except KeyboardInterrupt:
        pass
