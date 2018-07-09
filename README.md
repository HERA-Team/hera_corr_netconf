Some simple scripts to automate configuration of the various 40GbE switches in the HERA FX correlator.

To invoke, set up a config yaml file with VLANs and static mac-table mappings and:

1. Configure mac-table mappings with `python configure_address_table.py <config_file>`
2. Configure VLAN assignments with `python configure_vlans.py <config_file>`

To use this code you'll need the pyeapi module from https://github.com/arista-eosplus/pyeapi, and should
have enabled the http API on your switch(es) with:

```
Arista(config)# management api http-commands
Arista(config-mgmt-api-http-cmds)# no shutdown
Arista(config-mgmt-api-http-cmds)# protocol http
```
