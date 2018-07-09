import pyeapi
import yaml
import sys
import socket

def print_success(success):
    if success:
        print "SUCCEEDED!"
    else:
        print "FAILED!"

def format_mac_str(mac):
    """
    Format an integer MAC address into
    Arista's H.H.H hex format
    """
    hex_str = "%.12x" % mac
    return "%s.%s.%s" % (hex_str[0:4], hex_str[4:8], hex_str[8:12])

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

def lookup_mac(host):
    """
    Look up the mac address of `host`.
    Return it as an integer.
    """
    ip = map(int, socket.gethostbyname(host).split("."))
    ip = (ip[0] << 24) + (ip[1] << 16) + (ip[2] << 8) + ip[3]
    mac = 0x020200000000 + ip
    return mac

with open(sys.argv[1], 'r') as fh:
    config = yaml.load(fh.read())

arp_cache = {}
for host, conf in config['switches'].iteritems():
    print ''
    print 'Connecting to switch: %s' % host
    if "address_table" not in conf.keys():
        print 'Skipping %s because it has no static address table defined' % host
        continue
    switch = pyeapi.connect(host=host, username=conf['username'], password=conf['password'], return_node=True)
    for port, desthosts in conf['address_table'].iteritems():
        port_str = gen_port_str(conf['model'], port)
        for desthost in desthosts:
            if desthost in arp_cache.keys():
                mac = arp_cache[desthost]
            else:
                mac = lookup_mac(desthost)
                arp_cache[desthost] = mac
        print "Mapping destination mac 0x%x to port %s..." % (mac, port_str)
        mac_str = format_mac_str(mac)
        success = switch.config("mac address-table static %s vlan 1 interface Ethernet %s" % (mac_str, port_str))


