#!/usr/bin/env python

import redis
import yaml
import argparse
import pyeapi
import json
import datetime

parser = argparse.ArgumentParser(description='Write the output of a switch query to redis',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('config_file',type=str,
                    help = 'Configuration YAML file containing switch host/login details')
parser.add_argument('command', type=str,
                    help ='Switch command to run')
parser.add_argument('key', type=str,
                    help ='Redis key name to which command output should be written')
parser.add_argument('-r', dest='redishost', type=str, default='redishost',
                    help ='Hostname of redis server')
args = parser.parse_args()

with open(args.config_file, 'r') as fh:
    config = yaml.load(fh.read())

r = redis.Redis(args.redishost)

for host, conf in config['switches'].iteritems():
    print 'Connecting to switch: %s' % host
    redis_key = 'status:switch:%s' % host
    switch = pyeapi.connect(host=host, username=conf['username'], password=conf['password'], return_node=True)
    rv = switch.enable([args.command], encoding='text')
    string_table = rv[0]['result']['output']
    print string_table
    r.hset(redis_key, args.key, json.dumps({'timestamp':datetime.datetime.now().isoformat(), 'val':string_table}))
