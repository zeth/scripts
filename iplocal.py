#!/usr/bin/env python
"""Module for getting IP Addresses from the local computer.
This only works for Linux, but should always work despite what 
may or may not be in /etc/hosts. 
A cross-platform approach is to set up a dummy socket and inspect
the sockname.
This is based originally on a snippet from Charles G Waldman on the
mailing list.
http://mail.python.org/pipermail/python-list/1999-August/009153.html
Errors are my own."""

import socket
import fcntl

def get_ip_address():
    """Returns a dictionary of interfaces and IP Addresses."""
    iflist = open("/proc/net/dev").readlines()
    dummy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_addresses = {}
    for line in iflist:
        if ':' not in line:
            continue
        ifname = line.split(':')[0].strip()
        ifr = ifname + '\0'*(32-len(ifname))
        try:
            requ = fcntl.ioctl(dummy_sock.fileno(),
                               0x8915, # The magic SIOCGIFADDR
                               ifr)
        except IOError:
            print "Your loopback device may be dead."
            print "Check your system settings."
            
        addr = []
        for i in requ[20:24]: 
            addr.append(ord(i)) 
        ip_addresses[ifname] = addr
    return ip_addresses
        
def main():
    """When called directly, let's print the results in a 
    human readable format."""
    result = get_ip_address()
    for i in result:
        ient = ""
        for j in result[i]:
            ient += str(j) + '.'
        ient = ient.rstrip('.')
        print i, ient

# start the ball rolling
if __name__ == "__main__": 
    main()

