#!/usr/bin/env python

import pyeapi.api.vlans
import yaml
import sys

def print_success(success):
    if success:
        print "SUCCEEDED!"
    else:
        print "FAILED!"

def get_current_vlans(switch_vlan_api):
    return map(int, switch_vlan_api.keys())

def gen_port_str(model, port):
    """
    For a given switch model, generate a string which the switch
    will recognize as a particular interface.
    Eg, for a `model`='7050qx-32', port 32 -> '32', but port 14 -> '14/1'
    For broken out interfaces, `port` is a string (eg, '6/3')
    and this function does nothing.
    """
    if model.lower() == "7050qx-32":
        if type(port) is int:
            if port < 25:
                return "%d/1" % port
            else:
                return "%d" % port
        elif type(port) is str:
            return port
    else:
        print "I don't understand model %s!" % model
        exit

with open(sys.argv[1], 'r') as fh:
    config = yaml.load(fh.read())

for host, conf in config['switches'].iteritems():
    if "vlans" not in conf.keys():
        print 'Skipping %s because it has no vlans defined' % host
        continue
    print 'Connecting to switch: %s' % host
    switch = pyeapi.connect(host=host, username=conf['username'], password=conf['password'], return_node=True)
    vlan_api = switch.api('vlans')
    current_vlans = get_current_vlans(vlan_api)
    print "Current vlans:", current_vlans
    for port, vlans in conf['vlans'].iteritems():
        port_str = gen_port_str(conf['model'], port)
        if type(vlans) is int:
            vlan = vlans
            if (vlan not in current_vlans) and not vlan_api.get(vlan):
                print "Creating vlan %d" % vlan
                vlan_api.create(vlans)
                current_vlans = get_current_vlans(vlan_api)
            print "Adding Ethernet %s to vlan %d..." % (port_str, vlan),
            sys.stdout.flush()
            success = vlan_api.configure_interface('Ethernet %s' % port_str, ['switchport mode access', 'switchport access vlan %d' % vlan])
            print_success(success)
        elif type(vlans) is list:
            for vlan in vlans:
                if (vlan not in current_vlans) and not vlan_api.get(vlan):
                    print "Creating vlan %d" % vlan
                    vlan_api.create(vlan)
                    current_vlans = get_current_vlans(vlan_api)
            print "Setting Ethernet %s native vlan to %d" % (port_str, vlans[0]),
            sys.stdout.flush()
            success = vlan_api.configure_interface('Ethernet %s' % port_str, ['switchport mode trunk', 'switchport trunk native vlan %d' % vlans[0]])
            print_success(success)
            print "Adding Ethernet %s to tagged vlans %s..." % (port_str, ','.join(map(str, vlans[1:]))),
            sys.stdout.flush()
            success = vlan_api.configure_interface('Ethernet %s' % port_str, ['switchport mode trunk', 'switchport trunk allowed vlan %s' % ','.join(map(str, vlans))])
            print_success(success)


