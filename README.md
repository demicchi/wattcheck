# wattcheck 
## Overview
Unofficial logger for RS-WFWATTCH1 and RS-WFWATTCH2. 
This program collects measurements from RS-WFWATTCH1 and RS-WFWATTCH2 and stores the data into InfluxDB2.

## Warning
Commands defined in this program for RS-WFWATTCH1 and RS-WFWATTCH2 are observation-based, 
and there is no guarantee that the commands are correct.
You can use this program, but SORELY ON YOUR RESPONSIBILITY AT YOUR OWN RISK. 
Warranty of RS-WFWATTCH1 and RS-WFWATTCH2 may void.
This program is UNOFFICIAL. 
**NEVER contact the manufacture of RS-WFWATTCH1 and RS-WFWATTCH2 about this program nor any results by using this program.**

## Installation
python >= 3.12 and [influxdb-client](https://github.com/influxdata/influxdb-client-python) are required.
Below is an example for Ubuntu 24.04.

1. Install python >= 3.12
```
$ sudo apt update
$ sudo apt install python3 python3-venv
$ python3 -V
Python 3.12.3
```

2. (Optional but recommended) Create a dedicated system user. In this example `/opt/wattcheck` is the home directory of the system user `wattcheck`.
```
$ sudo useradd -rs /bin/bash -b /opt -m wattcheck
```

3. Clone this repository.
```
$ sudo -su wattcheck
wattcheck$ cd ~
wattcheck$ git clone "https://github.com/demicchi/wattcheck"
```

4. (Optional but strongly recommended) Create virtualenv.
```
wattcheck$ cd wattcheck
wattcheck$ python3 -m venv venv
wattcheck$ . venv/bin/activate
```

5. Install requirements.
```
(venv) wattcheck$ pip install -r requirements.txt 
```

6. Configure `settings.toml`.
```
(venv) wattcheck$ cp settings.sample.toml settings.toml
(venv) wattcheck$ vi settings.toml
```

7. (Optional but strongly recommended) Test this program.
```
(venv) wattcheck$ python wattcheck.py
```

You should now see the measurements in the Web UI of InfluxDB. 
If everything is ok, you can periodically execute this program by cron or systemd-timer.

8. Set periodical timer. In this example systemd-timer is used.
```
(venv) wattcheck$ exit
$ sudo cp doc/systemd-timer-sample/wattcheck.* /etc/systemd/system/
$ sudo vi /etc/systemd/system/wattcheck.timer
$ sudo vi /etc/systemd/system/wattcheck.service
```

You need to adjust values in `wattcheck.timer` and `wattcheck.service` to suit your environment.

```
$ sudo systemctl enable wattcheck.timer
$ sudo systemctl start wattcheck.timer
$ sudo systemctl list-timers
NEXT                            LEFT LAST                              PASSED UNIT                           ACTIVATES 
<<snip>>
Fri 2025-03-07 17:26:32 UTC      52s Fri 2025-03-07 17:25:32 UTC       7s ago wattcheck.timer                wattcheck.service
<<snip>>
$ 
```

## License
The project is available as open source under the terms of the [MIT License](https://opensource.org/license/mit).





