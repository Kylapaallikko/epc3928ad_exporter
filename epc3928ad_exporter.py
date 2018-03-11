#!/usr/bin/env python
"""epc3928ad_exporter.py current up- and downstream signal values from EPC3928AD."""
from sys import argv
from time import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from lxml import html

# Check if user gave necessary parameters
if len(argv) < 4:
    raise Exception('No arguments given. format: addr port modem')
# inits
MODEM_ADDR = argv[3]
LISTEN_ADDR = (argv[1], int(argv[2])) # addr, port

elements = ['ch_pwr', 'ch_snr', 'up_pwr']
help = {'ch_pwr': 'downstream power level',
        'ch_snr': 'downstream signal to noise ratio',
        'up_pwr': 'upstream power level',
        'collector_duration_seconds': 'duration in seconds'}

# https://docs.python.org/3.6/library/http.server.html?highlight=basehttprequesthandler
class http(BaseHTTPRequestHandler):
    help_type_format = "# HELP modem_{0} {1}\n# TYPE modem_{0} gauge\n"
    
    def _set_headers(self,code=200):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
    
    def do_HEAD(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == "/metrics":
            data = self.collect()
            if data:
                self._set_headers()
                for values in data:
                    self.wfile.write(self.help_type_format.format(values, help[values]).encode('utf-8'))
                    for i, value in enumerate(data[values]):
                            self.wfile.write(self.write_format(values).format(values, i+1, value).encode('utf-8'))
            else:
                self._set_headers(500)

    def collect(self):
        t = time()
        r = {}
        try:
            doc = html.parse("http://{}/Docsis_system.asp".format(MODEM_ADDR))
            for element in elements:
                data = doc.xpath('//td[contains(@headers, "{}")]/text()'.format(element))
                r[element] = [float(i) for i in data]
            r['collector_duration_seconds'] = [time()-t]
            return r
        except Exception:
            return None
    
    def write_format(self, values):
        template = 'modem_{0} {2}\n'
        if values in elements:
            template = 'modem_{0}{{channel="{1}"}} {2}\n'
        return template

# Code execution begins here!
httpd = HTTPServer(LISTEN_ADDR, http)
print('http server started {0[0]}:{0[1]}'.format(LISTEN_ADDR))
httpd.serve_forever()