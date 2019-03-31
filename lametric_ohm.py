#!/usr/bin/env/ python3
# coding=utf-8
#
# Parse OpenHardwareMonitor's Remote Data (JSON) and publish it to LaMetric
# Ganesh Velu

import time
import requests
import json
from collections import OrderedDict

# Configurables
OPENHARDWAREMONITOR_URL = "YOUR_COMPUTER_IP:8085/data.json"
LA_TOKEN = "YOUR_APP_TOKEN"
LA_PUSH_URL_LOCAL = "YOUR_LOCAL_PUSH_URL"

# Enter the Sensors here from HWiNFO in the same format
SENSORS = dict.fromkeys(
    ['CPU Package', 'GPU Temperature', 'T_Sensor1', 'Vcore']
    )

# Temperature thresholds for dynamic Icons
ICON_THRESHOLD_TEMP_HOT = 75
ICON_THRESHOLD_TEMP_COLD = 55

# Polling Interval
INTERVAL = 3
# End of Configurables

HEADERS = {'Accept': 'application/json', 'X-Access-Token': LA_TOKEN, "Cache-Control": "no-cache"}
FIRSTRUN = [True]
SENSORS_INDEX = {}


def scan_values():
    global SENSORS_INDEX
    print("Scanning for Sensors...")
    json_data = requests.get(OPENHARDWAREMONITOR_URL, verify=False, timeout=5).json()
    for i in range(0, len(json_data['hwinfo']['readings'])):
        for sensor in SENSORS:
            if json_data['hwinfo']['readings'][i]['labelOriginal'] == sensor:
                if (not SENSORS[sensor]): SENSORS[sensor] = json_data['hwinfo']['readings'][i]['entryIndex']

    # Sort the dictionary and replace the values with sorted index
    SENSORS_INDEX = OrderedDict(sorted(SENSORS.items(), key=lambda t: t[1]))
    for i in range(len(SENSORS_INDEX)):
        SENSORS_INDEX[list(SENSORS_INDEX)[i]] = i
    print("Scan complete!")


def push_hwinfo(json_data):
    # disable warning about the certificate for local push
    try:
        requests.packages.urllib3.disable_warnings()
        response = requests.post(LA_PUSH_URL_LOCAL, data=json.dumps(json_data), headers=HEADERS, verify=False, timeout=2)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
        print("Unable to reach LaMetric Time, check your connection")
    except Exception as e:
        print("Unexpected error! %s " % e)
        pass


def parse_ohm():
    # get the data from open hardware monitor (make sure port 8085 is open on windows firewall)
    try:
        if(FIRSTRUN[0]):
            FIRSTRUN[0] = False
            scan_values()

        json_data = requests.get(OPENHARDWAREMONITOR_URL + '?enable=' + ','.join(str(sensor) for sensor in SENSORS.values()), verify=False, timeout=3).json()

        # parse data to get appropriate values

        # CPU Package Temperature
        cpu_temp = json_data['hwinfo']['readings'][SENSORS_INDEX['CPU Package']]['value']

        # CPU Vcore
        cpu_vcore = json_data['hwinfo']['readings'][SENSORS_INDEX['Vcore']]['value']

        # GPU Temperature
        gpu_temp = json_data['hwinfo']['readings'][SENSORS_INDEX['GPU Temperature']]['value']

        # Custom Loop Coolant Temperature
        coolant_temp = json_data['hwinfo']['readings'][SENSORS_INDEX['T_Sensor1']]['value']

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
        json_data = {"frames": [{"text": "CPU " + str(cpu_temp)[:2] + "°", "icon": cpu_icon},
                                {"text": "GPU " + str(gpu_temp)[:2] + "°", "icon": gpu_icon},
                                {"text": "H2O " + str(coolant_temp)[:2] + "°", "icon": "a26855"},
                                {"text": "VC " + str(cpu_vcore)[:4], "icon": "a27512"}]}
        push_hwinfo(json_data)

    # See if System is up else report off-line on Lametric
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
        json_data = {"frames": [{"text": "SYSTEM OFFLINE", "icon": "a27513"}]}
        # json_data = {"frames": [{"text": "SYSTEM OFFLINE", "icon": "a22294"}]}
        push_hwinfo(json_data)
    except requests.exceptions.RequestException as e:
        print("Unexpected connection error: %s" % e)
    except (ValueError, IndexError):
        print("Unable to fetch CPU/GPU Temperature, check the json output to fix the keys.")


if __name__ == '__main__':
    try:
        while True:
            timed_start = time.time()
            parse_ohm()
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Shutting down!")
        pass
