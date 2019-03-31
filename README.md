<h1 align="center">
  <a href="https://github.com/iganeshk/LaMetric-System-Monitor/" title="LaMetric LaMetric System Monitor">
    <img alt="LaMetric-System-Monitor" src="https://github.com/iganeshk/LaMetric-System-Monitor/raw/master/demo.gif" width="80%" />
  </a>
  <br />
  LaMetric System Monitor
</h1>

<p align="center">
  Monitor your system vitals (Windows) on Lametric's Time.
</p>

<br />

## What is LaMetric System Monitor?

This utility parses the HWiNFO's data from it's json server and pushes it to LaMetric Time via an Indicator App.

## How to Use

#### Requirements

* LaMetric Developer Account with Time registered (Sign up here: [https://developer.lametric.com](https://developer.lametric.com/))
* HWiNFO - [https://www.hwinfo.com/download/](https://www.hwinfo.com/download/)
* [Python3](https://www.python.org/download/releases/3.0/)
* Python3 modules: requests, json and yaml (integration with home assistant)
<!-- * LibreHardwareMonitor (OpenHardwareMonitor fork): [https://ci.appveyor.com/project/LibreHardwareMonitor/librehardwaremonitor](https://ci.appveyor.com/project/LibreHardwareMonitor/librehardwaremonitor) -->

#### How to create an Indicator App?

* Follow this tutorial to create an Indicator App [https://lametric-documentation.readthedocs.io/en/latest/guides/first-steps/first-lametric-indicator-app.html](https://lametric-documentation.readthedocs.io/en/latest/guides/first-steps/first-lametric-indicator-app.html).
* Make sure to select `PUSH` as communication protocol and publish as `PRIVATE` app.
* Copy the local url (much advised for faster and reliable updates)

#### Usage

`python3 lametric_ohm.py`

#### Installation (systemd service for Linux Environment)

* We'll be using `screen` to monitor the script and run it as a service.
* Then create the systemd script by copying the following in to `/etc/systemd/system/lametric.service`. This will control the running of the service and allow it to run on startup. 

```
[Unit]
Description=Lametric Time System Monitor Screen
After=syslog.target network-online.target

[Service]
Type=forking
ExecStart=/usr/bin/screen -dmS lametric bash -c 'python3 /home/user/lametric_ohm.py'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

* Enable the `systemd` service to run on startup, then start the service and check its status. 
* To grab the screen and monitor the service, 
```screen -r lametric```
* To exit the screen, try the key combination `CTRL+D` to get out.