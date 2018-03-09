#!/usr/bin/env python
"""epc3928ad_exporter.py current up- and downstream signal values from EPC3928AD."""
from sys import argv
from http.server import BaseHTTPRequestHandler, HTTPServer
from lxml import html

__author__ = "Kyläpäällikkö"
__copyright__ = "Copyright 2018, Kyläpäällikkö"
__license__ = "MIT"
__version__ = "1.0"

# Check if user gave necessary parameters
if len(argv) < 4:
    raise Exception('No arguments given. format: addr port modem')
# inits
MODEM_ADDR = argv[3]
LISTEN_ADDR = (argv[1], int(argv[2])) # addr, port

# https://docs.python.org/3.6/library/http.server.html?highlight=basehttprequesthandler
class http(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
    
    def log_request(self, code="", size=""):
        pass

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        if self.path == "/metrics":
            data = self.fetch()
            for values in data:
                i = 1
                self.wfile.write(self.help_type(values).encode('utf-8'))
                for value in data[values]:
                    self.wfile.write(('modem_%s{channel="%s"} %s\n' % (values, i, value)).encode('utf-8'))
                    i += 1
        else:
            self.wfile.write("/metrics".encode('utf-8'))

    def help_type(self, value):
        if value == "down_pwr":
            return '# HELP modem_down_pwr Current dowmstream power level\n# TYPE modem_down_pwr gauge\n'
        elif value == "down_snr":
            return '# HELP modem_down_snr Current dowmstream signal to noise ratio\n# TYPE modem_down_snr gauge\n'
        elif value == "up_pwr":
            return '# HELP modem_up_pwr Current upstream power level\n# TYPE modem_up_pwr gauge\n'

    def fetch(self):
        try:
            doc = html.parse('http://%s/Docsis_system.asp' % MODEM_ADDR)
        except Exception as e:
            raise Exception(e)
        # DOWN
        PWR = doc.xpath('//td[contains(@headers, "ch_pwr")]/text()')
        SNR = doc.xpath('//td[contains(@headers, "ch_snr")]/text()')
        # UP
        UP = doc.xpath('//td[contains(@headers, "up_pwr")]/text()')
        # Remove whitespaces. translate and normalize_space has unexpected behavior with negative values.
        for values in [PWR, SNR, UP]:
            i = 0
            for value in values:
                values[i] = value.replace(" ","")
                i += 1
        # Returns
        return {'down_pwr': PWR,
                'down_snr': SNR,
                'up_pwr': UP}

# Code execution begins here!
httpd = HTTPServer(LISTEN_ADDR, http)
print('http server started %s:%s' % LISTEN_ADDR)
httpd.serve_forever()