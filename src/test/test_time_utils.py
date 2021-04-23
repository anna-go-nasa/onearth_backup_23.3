#!/usr/bin/env python3

# Copyright (c) 2002-2020, California Institute of Technology.
# All rights reserved.  Based on Government Sponsored Research under contracts NAS7-1407 and/or NAS7-03001.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#   3. Neither the name of the California Institute of Technology (Caltech), its operating division the Jet Propulsion Laboratory (JPL),
#      the National Aeronautics and Space Administration (NASA), nor the names of its contributors may be used to
#      endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE CALIFORNIA INSTITUTE OF TECHNOLOGY BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Tests for time utilities
#

import os
import sys
import unittest2 as unittest
import xmlrunner
from optparse import OptionParser
from subprocess import Popen, PIPE
import time
import redis
import requests
import shutil
from oe_test_utils import restart_apache, make_dir_tree, mrfgen_run_command as run_command

DEBUG = False

DATE_SERVICE_LUA_TEMPLATE = """local onearthTimeService = require "onearthTimeService"
handler = onearthTimeService.timeService({handler_type="redis", host="127.0.0.1"}, {filename_format="hash"})
"""

DATE_SERVICE_APACHE_TEMPLATE = """Alias /date_service {config_path}

<IfModule !ahtse_lua>
        LoadModule ahtse_lua_module modules/mod_ahtse_lua.so
</IfModule>

<Directory {config_path}>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
        AHTSE_lua_RegExp date_service
        AHTSE_lua_Script {config_path}/date_service.lua
        AHTSE_lua_Redirect On
        AHTSE_lua_KeepAlive On
</Directory>
"""


def redis_running():
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        return r.ping()
    except redis.exceptions.ConnectionError:
        return False


def seed_redis_data(layers, db_keys=None):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    db_keystring = ''
    if db_keys:
        for key in db_keys:
            db_keystring += key + ':'
 
    for layer in layers:
        r.zadd('{0}layer:{1}:dates'.format(db_keystring, layer[0]), {layer[1]:0})
            
    with open('periods.lua', 'r') as f:
        lua_script = f.read()
    date_script = r.register_script(lua_script)
    date_script(keys=['{0}layer:{1}'.format(db_keystring, layer[0])])


def remove_redis_layer(layer, db_keys=None):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    db_keystring = ''
    if db_keys:
        for key in db_keys:
            db_keystring += key + ':'
    r.delete('{0}layer:{1}:default'.format(db_keystring, layer[0]))
    r.delete('{0}layer:{1}:periods'.format(db_keystring, layer[0]))
    r.delete('{0}layer:{1}:config'.format(db_keystring, layer[0]))
    
    
def add_redis_config(layers, db_keys, config):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    db_keystring = ''
    if db_keys:
        for key in db_keys:
            db_keystring += key + ':'
    r.sadd('{0}layer:{1}:config'.format(db_keystring, layers[0][0]), config)


class TestTimeUtils(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Check if mod_ahtse_lua is installed
        apache_path = '/etc/httpd/modules/'
        if not os.path.exists(os.path.join(apache_path, 'mod_ahtse_lua.so')):
            print("WARNING: Can't find mod_ahtse_lua installed in: {0}. Tests may fail.".format(apache_path))

        # Check if onearth Lua stuff has been installed
        lua = Popen(['luarocks', 'list'], stdout=PIPE)
        (output, _) = lua.communicate()
        p_status = lua.wait()
        if p_status:
            print("WARNING: Error running Luarocks. Make sure lua and luarocks are installed and that the OnEarth lua package is also installed. Tests may fail.")
        if 'onearth' not in str(output):
            print("WARNING: OnEarth luarocks package not installed. Tests may fail.")

        # Start redis
        if not redis_running():
            Popen(['redis-server'])
        time.sleep(2)
        if not redis_running():
            print("WARNING: Can't access Redis server. Tests may fail.")

        # Copy Lua config
        test_lua_config_dest_path = '/build/test/ci_tests/tmp/date_service_test'
        test_lua_config_filename = 'date_service.lua'
        self.test_lua_config_location = os.path.join(test_lua_config_dest_path,
                                                     test_lua_config_filename)

        make_dir_tree(test_lua_config_dest_path, ignore_existing=True)
        with open(self.test_lua_config_location, 'w+') as f:
            f.write(DATE_SERVICE_LUA_TEMPLATE)

        # Copy Apache config
        self.test_config_dest_path = os.path.join(
            '/etc/httpd/conf.d', 'oe2_test_date_service.conf')
        with open(self.test_config_dest_path, 'w+') as dest:
            dest.write(
                DATE_SERVICE_APACHE_TEMPLATE.replace(
                    '{config_path}', test_lua_config_dest_path))

        self.date_service_url = 'http://localhost/date_service/date?'

        restart_apache()
        
        shutil.copyfile("/home/oe2/onearth/src/modules/time_service/utils/periods.lua", os.getcwd() + '/periods.lua')

    def test_time_scrape_s3_keys(self):
        # Test scraping S3 keys
        test_layers = [('Test_Layer', '2017-01-04',
                        '2017-01-01/2017-01-04/P1D')]
        
        cmd = "python3.6 /home/oe2/onearth/src/modules/time_service/utils/oe_scrape_time.py -r -t best -b test-bucket 127.0.0.1"
        run_command(cmd, True)
        db_keys = ['epsg4326', 'best']
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[1], layer_res['default'],
                'Layer {0} has incorrect "default" value -- got {1}, expected {2}'
                .format(layer[0], layer[1], layer_res['default']))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)

    def test_time_scrape_s3_inventory(self):
        # Test scraping S3 inventory file
        test_layers = [('MODIS_Aqua_CorrectedReflectance_TrueColor', '2017-01-15',
                        '2017-01-01/2017-01-15/P1D'),
                       ('MODIS_Aqua_Aerosol', '2017-01-15',
                       '2017-01-01T00:00:00Z/2017-01-15T00:00:00Z/PT1S')]
        
        cmd = "python3.6 /home/oe2/onearth/src/modules/time_service/utils/oe_scrape_time.py -i -r -t best -b test-inventory 127.0.0.1"
        run_command(cmd, True)
        db_keys = ['epsg4326', 'best']
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[1], layer_res['default'],
                'Layer {0} has incorrect "default" value -- got {1}, expected {2}'
                .format(layer[0], layer[1], layer_res['default']))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer[2], layer_res['periods'][0]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_single_date(self):
        # Test adding layer with single date
        test_layers = [('Test_Single', '2019-01-15',
                        '2019-01-15/2019-01-15/P1D')]

        db_keys = ['epsg4326', 'best']        
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[1], layer_res['default'],
                'Layer {0} has incorrect "default" value -- got {1}, expected {2}'
                .format(layer[0], layer[1], layer_res['default']))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer[2], layer_res['periods'][0]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_subdaily(self):
        # Test subdaily period
        test_layers = [('Test_Subdaily', '2020-01-01T00:00:00Z',
                        '2020-01-01T00:00:00Z/2020-01-01T00:00:01Z/PT1S')]

        db_keys = ['epsg4326', 'best']        
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[1], layer_res['default'],
                'Layer {0} has incorrect "default" value -- got {1}, expected {2}'
                .format(layer[0], layer[1], layer_res['default']))
            
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_multiday(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_Multiday', '2019-01-01',
                        '2019-01-01/2019-01-19/P6D'),
                       ('Test_Multiday', '2019-01-07',
                        '2019-01-01/2019-01-19/P6D'),
                       ('Test_Multiday', '2019-01-13',
                        '2019-01-01/2019-01-19/P6D'),
                       ('Test_Multiday', '2019-01-19',
                        '2019-01-01/2019-01-19/P6D')]

        db_keys = ['epsg4326', 'best']        
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer[2], layer_res['periods'][0]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_monthly(self):
        # Test adding layer with multiple months
        test_layers = [('Test_Monthly', '2019-01-01',
                        '2019-01-01/2019-04-01/P1M'),
                       ('Test_Monthly', '2019-02-01',
                        '2019-01-01/2019-04-01/P1M'),
                       ('Test_Monthly', '2019-03-01',
                        '2019-01-01/2019-04-01/P1M'),
                       ('Test_Monthly', '2019-04-01',
                        '2019-01-01/2019-04-01/P1M')]

        db_keys = ['epsg4326', 'best']
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer[2], layer_res['periods'][0]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_DETECT(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_DETECT', '2019-01-01',
                        '2019-01-01/2019-01-13/P6D'),
                       ('Test_DETECT', '2019-01-07',
                        '2019-01-01/2019-01-13/P6D'),
                       ('Test_DETECT', '2019-01-13',
                        '2019-01-01/2019-01-13/P6D')]
        db_keys = ['epsg4326', 'best']
        config = 'DETECT'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_DETECTDETECT(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_DETECTDETECT', '2019-01-01',
                        '2019-01-01/2019-01-13/P6D'),
                       ('Test_DETECTDETECT', '2019-01-07',
                        '2019-01-01/2019-01-13/P6D'),
                       ('Test_DETECTDETECT', '2019-01-13',
                        '2019-01-01/2019-01-13/P6D')]
        db_keys = ['epsg4326', 'best']
        config = 'DETECT/DETECT'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_DETECTDETECTP5D(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_DETECTDETECTP5D', '2019-01-01',
                        '2019-01-01/2019-01-13/P5D'),
                       ('Test_DETECTDETECTP5D', '2019-01-07',
                        '2019-01-01/2019-01-13/P5D'),
                       ('Test_DETECTDETECTP5D', '2019-01-13',
                        '2019-01-01/2019-01-13/P5D')]
        db_keys = ['epsg4326', 'best']
        config = 'DETECT/DETECT/P5D'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_DETECTP10D(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_DETECTP10D', '2019-01-01',
                        '2019-01-01/2019-01-13/P10D'),
                       ('Test_DETECTP10D', '2019-01-07',
                        '2019-01-01/2019-01-13/P10D'),
                       ('Test_DETECTP10D', '2019-01-13',
                        '2019-01-01/2019-01-13/P10D')]
        db_keys = ['epsg4326', 'best']
        config = 'DETECT/P10D'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_force_all(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_ForceAll', '2019-01-01',
                        '2017-01-01/2020-12-01/P8D'),
                       ('Test_ForceAll', '2019-01-07',
                        '2017-01-01/2020-12-01/P8D'),
                       ('Test_ForceAll', '2019-01-13',
                        '2017-01-01/2020-12-01/P8D')]
        db_keys = ['epsg4326', 'best']
        config = '2017-01-01/2020-12-01/P8D'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_force_start(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_ForceStart', '2019-01-01',
                        '2017-01-01T00:00:00Z/2019-01-13T:23:59:59Z/PT1M'),
                       ('Test_ForceStart', '2019-01-07',
                        '2017-01-01T00:00:00Z/2019-01-13T:23:59:59Z/PT1M'),
                       ('Test_ForceStart', '2019-01-13T:23:59:59',
                        '2017-01-01T00:00:00Z/2019-01-13T:23:59:59Z/PT1M')]
        db_keys = ['epsg4326', 'best']
        config = '2017-01-01/DETECT/PT1M'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_force_end(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_ForceEnd', '2019-01-01',
                        '2019-01-01/2020-12-01/P1M'),
                       ('Test_ForceEnd', '2019-01-07',
                        '2019-01-01/2020-12-01/P1M'),
                       ('Test_ForceEnd', '2019-01-13',
                        '2019-01-01/2020-12-01/P1M')]
        db_keys = ['epsg4326', 'best']
        config = 'DETECT/2020-12-01/P1M'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for layer in test_layers:
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][0],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][0], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)
                
    def test_periods_config_multiple(self):
        # Test adding layer with multiple dates
        test_layers = [('Test_Multiple', '2019-01-01',
                        '2016-01-01/2017-12-31/P1D'),
                       ('Test_Multiple', '2019-01-02',
                        '2019-01-01/2019-01-04/P1D'),
                       ('Test_Multiple', '2019-01-03',
                        '2019-01-02/2019-01-04/P1D'),
                       ('Test_Multiple', '2019-01-04',
                        '2022-01-01/2022-12-01/P1M')]
        db_keys = ['epsg4326', 'best']
        # forced period
        config = '2016-01-01/2017-12-31/P1D'
        add_redis_config(test_layers, db_keys, config)
        # detect 2019-01-01 as start
        config = 'DETECT/2019-01-04/P1D'
        add_redis_config(test_layers, db_keys, config)
        # detect 2019-01-04 as end
        config = '2019-01-02/DETECT/P1D'
        add_redis_config(test_layers, db_keys, config)
        # forced period
        config = '2022-01-01/2022-12-01/P1M'
        add_redis_config(test_layers, db_keys, config)
        seed_redis_data(test_layers, db_keys=db_keys)
        r = requests.get(self.date_service_url + 'key1=epsg4326&key2=best')
        res = r.json()
        for i, layer in enumerate(test_layers):
            layer_res = res.get(layer[0])
            self.assertIsNotNone(
                layer_res,
                'Layer {0} not found in list of all layers'.format(layer[0]))
            self.assertEqual(
                layer[2], layer_res['periods'][i],
                'Layer {0} has incorrect "period" value -- got {1}, expected {2}'
                .format(layer[0], layer_res['periods'][i], layer[2]))
            if not DEBUG:
                remove_redis_layer(layer, db_keys)

    @classmethod
    def tearDownClass(self):
        if not DEBUG:
            os.remove(self.test_config_dest_path)
            os.remove(self.test_lua_config_location)
            os.remove(os.getcwd() + '/periods.lua')


if __name__ == '__main__':
    # Parse options before running tests
    parser = OptionParser()
    parser.add_option(
        '-o',
        '--output',
        action='store',
        type='string',
        dest='outfile',
        default='test_time_utils_results.xml',
        help='Specify XML output file (default is test_time_utils_results.xml'
    )
    parser.add_option(
        '-d',
        '--debug',
        action='store_true',
        dest='debug',
        help='Output verbose debugging messages')
    (options, args) = parser.parse_args()

    DEBUG = options.debug

    # Have to delete the arguments as they confuse unittest
    del sys.argv[1:]

    with open(options.outfile, 'wb') as f:
        print('\nStoring test results in "{0}"'.format(options.outfile))
        unittest.main(testRunner=xmlrunner.XMLTestRunner(output=f))