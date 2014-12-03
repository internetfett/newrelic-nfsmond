import ConfigParser
import httplib
import json
import logging
import os
import time
import urllib2

from __init__ import __version__


class NFSPlugin(object):
    def __init__(self, conf='/etc/newrelic-nfsmond.conf'):
        # Constants
        self.guid = 'com.internetfett.nfsmond'
        self.name = 'NFS Disks'
        self.api_url = 'https://platform-api.newrelic.com/platform/v1/metrics'
        self.version = __version__
        self.conf = conf
        self.duration = 0
        self.duration_start = int(time.time())

        # System
        self.uname = os.uname()
        self.pid = os.getpid()
        self.hostname = self.uname[1]

        # Data
        self.metric_data = {}
        self.json_data = {}

        self._parse_config()
        self._build_agent_stanza()

    def _parse_config(self):
        config = ConfigParser.RawConfigParser()
        dataset = config.read(self.conf)
        if len(dataset) < 1:
            raise ValueError, "Failed to open/find config files"

        logfilename = config.get('plugin', 'logfile')
        loglevel = config.get('plugin', 'loglevel')
        logging.basicConfig(
            filename=logfilename,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s:%(funcName)s: %(message)s',
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)

        try:
            self.license_key = config.get('plugin', 'key')
            self.pid_file = config.get('plugin', 'pidfile')
            self.interval = config.get('plugin', 'interval')
            self.filesystem_type = config.get('plugin', 'filesystem_type')
        except Exception, e:
            self.logger.exception(e)
            raise e

    def _update_stats(self):
        command = "df -P -T " + self.filesystem_type
        output = os.popen(command).read().splitlines()
        for idx, line in enumerate(output[1:]):
            try:
                device, size, used, available, percent, mountpoint = line.split()
                prefix = 'Component/NFS/Volume' + mountpoint
                self.metric_data = {
                    prefix + '/Size[bytes]': size,
                    prefix + '/Used[bytes]': used,
                    prefix + '/Available[bytes]': available,
                    prefix + '/Percent': percent,
                }
            except ValueError:
                pass
            except Exception, e:
                self.logger.exception(e)
                raise e

    def _build_agent_stanza(self):
        """ Build the 'agent' stanza of the new relic json call """
        try:
            values = {}
            values['host'] = self.hostname
            values['pid'] = self.pid
            values['version'] = self.version
            self.json_data['agent'] = values
        except Exception, e:
            self.logger.exception(e)
            raise e

    def _build_component_stanza(self):
        """ Build the 'component' stanza for the new relic json call """
        try:
            self.duration =  int(time.time()) - self.duration_start
            c_list = []
            c_dict = {}
            c_dict['name'] = self.hostname
            c_dict['guid'] = self.guid
            c_dict['duration'] = self.duration

            self._update_stats()

            c_dict['metrics'] = self.metric_data
            c_list.append(c_dict)

            self.json_data['components'] = c_list
        except Exception, e:
            self.logger.exception(e)
            raise e

    def _reset_json_data(self):
        """ Reset the json data structure and prepare for the next call. """
        try:
            self.metric_data = {}
            self.json_data = {}
            self._build_agent_stanza()
        except Exception, e:
            self.logger.exception(e)
            raise e

    def add_to_newrelic(self):
        """ Send json request to New Relic """
        self._build_component_stanza()
        try:
            request = urllib2.Request(self.api_url)
            request.add_header("X-License-Key", self.license_key)
            request.add_header("Content-Type", "application/json")
            request.add_header("Accept", "application/json")

            opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.HTTPSHandler())
            response = opener.open(request, json.dumps(self.json_data))

            if response.code == 200:
                self.duration_start = int(time.time())
            response.close()

        except httplib.HTTPException, e:
            self.logger.error('HTTP Exception: %s' % e)
            pass

        except urllib2.HTTPError, e:
            self.logger.error('HTTP Error: %s' % e)
            self.logger.debug('HTTP Error Details: %s' % e.read())
            pass

        except urllib2.URLError, e:
            self.logger.error('URL Error: %s' % e.reason)
            pass

        self._reset_json_data
