# check_speedport_hybrid.py
checkmk datasource program for speedport hybrid.

checkmk
https://mathias-kettner.com/
Successfully tested on checkmk RAW version 1.6.0 (stable)

Path
----
- Place this into /omd/sites/<SITE>/local/bin/
- Make this script executable!

Configure
---------
WATO -> Datasource Programs -> Individual program call instead of agent access -> Command line to execute

```
check_speedport_hybrid.py --host $HOSTADDRESS$
```

Local network http links without authentication
-----------------------------------------------
HTML: http://<speedport-address>/html/login/status.html?lang=en
JSON: http://<speedport-address>/data/Status.json
