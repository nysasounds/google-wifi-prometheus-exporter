#!/usr/bin/env python3

import sys
import os
import requests


METRIC_TEMPLATE = '''\
# HELP {metric} {metric_desc}
# TYPE {metric} {metric_type}
{metric}{metric_labels} {metric_value}
'''


# Get router address frpm env #
router = os.environ.get('GOOGLE_WIFI_ROUTER')

# Or as arg #
if not router:
    try:
        router = sys.argv[1]
    except IndexError:
        print('No router IP or host provided', file=sys.stderr)
        sys.exit(1)


class Google_Wifi_Exporter():

    def __init__(self, router, prefix='google_wifi'):

        self.router = router
        self.prefix = prefix

    def get_status(self):
        '''
        Get router status from API
        Returns the status data as a hash
        '''

        try:
            status_response = requests.get(
                    'http://{router}/api/v1/status'.format(
                        router=self.router
                        )
                    )

            status_response.raise_for_status()
            return status_response.json()
        except Exception as err:
            print('Could not retrieve status from router: {}'.format(
                    err,
                    file=sys.stderr,
                )
            )
            sys.exit(1)

    def create_exporter(self, metric, metric_desc, metric_type, metric_value, metric_labels=None):
        '''
        Create exporter entries from template
        Returns formatted string to export
        '''

        # Addend prefix #
        metric = self.prefix + '_' + metric

        # Build any labels #
        if metric_labels:
            _labels = []
            for label, value in metric_labels.items():
                _labels.append('{label}="{value}"'.format(
                    label = label,
                    value = value,
                    )
                )

            metric_labels = '{' + ','.join(_labels) + '}'

        else:

            metric_labels = ''

        # Return string formatted from template #
        return(
                METRIC_TEMPLATE.format(
                    metric = metric,
                    metric_desc = metric_desc,
                    metric_type = metric_type,
                    metric_value = metric_value,
                    metric_labels = metric_labels,
                )
            )

    def build_metrics(self, status):
        '''
        Bulid the metrics from the status data
        Returns a hash of the metrics
        '''

        metrics = {}

        metrics['system_info'] = {
                'metric_desc': 'System Info',
                'metric_type': 'gauge',
                'metric_value': 1,
                'metric_labels': {
                    'led_status': status.get('system').get('ledAnimation'),
                    'lan_link': status.get('system').get('lan0Link'),
                    }
                }

        metrics['system_uptime_seconds'] = {
                'metric_desc': 'System Uptime in Secs',
                'metric_type': 'counter',
                'metric_value': status.get('system').get('uptime'),
                }

        metrics['software_info'] = {
                'metric_desc': 'Software Info',
                'metric_type': 'gauge',
                'metric_value': 1,
                'metric_labels': {
                    'blocking_update': bool(status.get('software').get('blockingUpdate')),
                    'software_version': status.get('software').get('softwareVersion'),
                    'update_channel': status.get('software').get('updateChannel'),
                    'update_new_version': status.get('software').get('updateNewVersion'),
                    'update_progress': status.get('software').get('updateProgress'),
                    'update_required': status.get('software').get('updateRequired'),
                    'update_status': status.get('software').get('updateStatus'),
                    }
                }

        metrics['wan_info'] = {
                'metric_desc': 'WAN Info',
                'metric_type': 'gauge',
                'metric_value': 1,
                'metric_labels': {
                    'captive_portal': status.get('wan').get('captivePortal'),
                    'ethernet_link': status.get('wan').get('ethernetLink'),
                    'invalid_credentials': status.get('wan').get('invalidCredentials'),
                    'has_local_ip': status.get('wan').get('ipAddress'),
                    'gateway_ip': status.get('wan').get('gatewayIpAddress'),
                    'local_ip': status.get('wan').get('localIpAddress'),
                    'primary_primary_server': status.get('wan').get('nameServers')[0],
                    'secondary_primary_server': status.get('wan').get('nameServers')[1],
                    'online': status.get('wan').get('online'),
                    'pppoe_detected': status.get('wan').get('pppoeDetected'),
                    }
                }

        metrics['dns_info'] = {
                'metric_desc': 'DNS Info',
                'metric_type': 'gauge',
                'metric_value': 1,
                'metric_labels': {
                    'mode': status.get('dns').get('mode'),
                    'primary_server': status.get('dns').get('servers')[0],
                    'secondary_server': status.get('dns').get('servers')[1],
                    }
                }

        return metrics

    def export(self, metrics):
        '''
        Print metrics from the provided as a hash of data
        '''

        for metric in metrics.keys():
            print(
                    self.create_exporter(
                        metric=metric,
                        **metrics[metric],
                    ),
                    end='',
            )

    def run(self):
        '''
        Exporter
        '''

        status = self.get_status()
        metrics = self.build_metrics(status=status)
        self.export(metrics=metrics)


if __name__ == '__main__':

    google_wifi = Google_Wifi_Exporter(router=router)
    google_wifi.run()
