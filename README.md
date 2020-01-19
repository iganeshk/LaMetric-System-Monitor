<h2 align="center">
  <a href="https://github.com/iganeshk/LaMetric-System-Monitor/" title="LaMetric LaMetric System Monitor">
    <img alt="LaMetric-System-Monitor" src="../assets/demo.gif?raw=true" width="80%" />
  </a>
  <br />
  LaMetric System Monitor
</h2>
<p align="center">
  Monitor your system metrics (Windows) on Lametric's Time.
</p>

<br />

## What is LaMetric System Monitor?

This utility parses the HWiNFO's data from [remotehwinfo](https://github.com/Demion/remotehwinfo)'s json server and pushes it to LaMetric Time via an Indicator App.

## How to Use

#### Requirements

* LaMetric Developer Account with Time registered (Sign up here: [https://developer.lametric.com](https://developer.lametric.com/))
* HWiNFO - [https://www.hwinfo.com/download/](https://www.hwinfo.com/download/)
* [HWiNFO JSON Web Server](https://github.com/Demion/remotehwinfo/releases/latest)
* [Python3](https://www.python.org/download/releases/3.0/)
* Python3 modules: requests, json and yaml (integration with home assistant)

#### How to create an Indicator App?

* Follow this tutorial to create an Indicator App [https://lametric-documentation.readthedocs.io/en/latest/guides/first-steps/first-lametric-indicator-app.html](https://lametric-documentation.readthedocs.io/en/latest/guides/first-steps/first-lametric-indicator-app.html).
* Make sure to select `PUSH` as communication protocol and publish as `PRIVATE` app.
* Copy the local url (much advised for faster and reliable updates)

#### Usage

* Fork this repository:
    ```
    $ git clone https://github.com/iganeshk/LaMetric-System-Monitor.git
    $ cd LaMetric-System-Monitor
    $ pip3 install -r requirements.txt
    ```
* Configure the following in `lametricSysMon.py`  using any editor:
    ```
    # Connection
    REMOTE_MONITOR_IP = ""                      # Default: 127.0.0.1
    REMOTE_MONITOR_PORT = ""                    # Default: 8085

    # LaMetric Credentials
    LA_TOKEN = "YOUR_APP_TOKEN"
    LA_PUSH_URL_LOCAL = "YOUR_LOCAL_PUSH_URL"   # Prefer local address if app running on a local network
    ```
* Run the following command on your system or raspberrypi or any python3 installed environment with local network access.
    ```
    $ python3 lametricSysMon.py
    ```

#### Installation (systemd service for Linux Environment)

* Then we create a `systemd` (service manager) script by copying the following in to `/etc/systemd/system/lametric.service`. 
* Confirm your `python3` path by running `which python3`.
    ```
    [Unit]
    Description=Lametric Time System Monitor Screen
    After=syslog.target network-online.target

    [Service]
    Type=forking
    ExecStart=/usr/bin/nice -n 19 '/usr/bin/python3 /root/lametricSysMon.py'
    Restart=always
    RestartSec=5
    KillMode=process

    [Install]
    WantedBy=multi-user.target
    ```
* Enable the `systemd` service to run on startup, then start the service and check its status. (by default set to run at startup)
    ```
    sudo systemctl daemon-reload
    sudo systemctl enable lametric
    sudo systemctl start lametric
    sudo systemctl status lametric
    ```


#### Remote HWiNFO Installation

* Grab the latest release and extract the executable. 
* Make sure HWiNFO is running and set to start up with Windows.
* Create the following task in the scheduler with highest privileges with "At Start Up" with the following flags:
    * Security Options: Run whether user logged in or not (with credentials)
    * Trigger: At Start Up
    * Action: Start a Program
        * Program/Script Path: Executable Path
        * Arguments: `-port 8085 -hwinfo 1 -gpuz 0 -afterburner 0 -log 0`
        * Start In: Executable Path
* Open port `8085` in the Windows Firewall for private network
