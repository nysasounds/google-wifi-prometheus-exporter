# google-wifi and prometheus exporter

Get basic system stats from you Google Wifi router, and expose stats for collecting via prometheus.

This is a docker container which creates a prometheus exporter from the output of router v1/status API.

This should work for all Woogle Wifi models, as the API has been around for a while.  But, tested on:
- Google Nest Wifi Pro

The exporter is implemented using https://github.com/ricoberger/script_exporter

## Stats

The metrics exported include:
- `system_info`
  - Includes a number of labels with info about the system status
- `system_uptime_seconds`
- `software_info`
  - Includes a number of labels with info about the software status and version
- `wan_info`
  - Includes a number of labels with info about the WAN connectivity and config
- `dns_info`
  - Includes a number of labels with info about the DNS mode and servers

The exported output looks like this:

```
# HELP google_wifi_system_info System Info
# TYPE google_wifi_system_info gauge
google_wifi_system_info{led_status={string},lan_link={bool}} 1

# HELP google_wifi_system_uptime_seconds System Uptime in Secs
# TYPE google_wifi_system_uptime_seconds counter
google_wifi_system_uptime_seconds {string}

# HELP google_wifi_software_info Software Info
# TYPE google_wifi_software_info gauge
google_wifi_software_info{blocking_update={bool},software_version={string},update_channel={string},update_new_version={string},update_progress={string},update_required={bool},update_status={string}} 1

# HELP google_wifi_wan_info WAN Info
# TYPE google_wifi_wan_info gauge
google_wifi_wan_info{captive_portal={bool},ethernet_link={bool},invalid_credentials={bool},has_local_ip={bool},gateway_ip={string},local_ip={string},primary_primary_server={string},secondary_primary_server={string},online=True,pppoe_detected={bool}} 1

# HELP google_wifi_dns_info DNS Info
# TYPE google_wifi_dns_info gauge
google_wifi_dns_info{mode={string},primary_server={string},secondary_server={string}} 1
```

## Testing

Run the container:
```
$ docker run --rm -p 9469:9469 -e GOOGLE_WIFI_ROUTER={ROUTER_IP} nysasounds/google-wifi-prometheus-exporter:0.0.1
```

Test the exporter.
It will return the export output,and of course your output will vary.
```
$ curl "http://localhost:9469/probe?script=google-wifi"

# HELP google_wifi_system_info System Info
# TYPE google_wifi_system_info gauge
google_wifi_system_info{led_status=CONNECTED,lan_link=True} 1
# HELP google_wifi_system_uptime_seconds System Uptime in Secs
# TYPE google_wifi_system_uptime_seconds counter
google_wifi_system_uptime_seconds 546345
# HELP google_wifi_software_info Software Info
# TYPE google_wifi_software_info gauge
google_wifi_software_info{blocking_update=True,software_version=1.23.456789,update_channel=stable-channel,update_new_version=0.0.0.0,update_progress=0.0,update_required=False,update_status=idle} 1
# HELP google_wifi_wan_info WAN Info
# TYPE google_wifi_wan_info gauge
google_wifi_wan_info{captive_portal=False,ethernet_link=True,invalid_credentials=False,has_local_ip=True,gateway_ip=1.2.3.4,local_ip=1.2.3.5,primary_primary_server=4.3.2.1,secondary_primary_server=4.3.2.2,online=True,pppoe_detected=True} 1
# HELP google_wifi_dns_info DNS Info
# TYPE google_wifi_dns_info gauge
google_wifi_dns_info{mode=automatic,primary_server=4.3.2.1,secondary_server=4.3.2.2} 1
```

## Prometheus

Example prometheus config could like something like this:

```
global:
  scrape_interval: 5m

scrape_configs:
  - job_name: 'google-wifi'
    static_configs:
      - targets:
        - "google-wifi:9469"
    metrics_path: "/probe"
    params:
      script: ["google-wifi"]
    scrape_timeout: "1m"
    relabel_configs:
      - target_label: script
        replacement: google-wifi

remote_write:
- url: https://prometheus-server
  bearer_token: some-super-secret-token
```

## Docker Compose Stack

You might want to create a small stack with this container and a prometheus container, which sends metrics to a remote prometheus ingestion somewhere, perhaps New Relic or any other prometheus ingestion provider.

There is an example docker-compose stack here: https://github.com/nysasounds/google-wifi-stack
