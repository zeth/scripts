"""ipaddress.py - IP address operations.
These functions deal with IPv4 addresses in integer forms.
This is useful in interoperating with MySQL/PHP applications
where these integer forms seem to be popular."""

# Redistribution and use in source and binary forms, 
# with or without modification, are permitted, subject
# to the terms and conditions of any software licence 
# that qualifies as a 'free software license' according to 
# the following web page:
# http://www.gnu.org/philosophy/license-list.html
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF 
# ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT

__author__ = 'Zeth'
__copyright__ = 'Copyright (C) 2009'
__version__ = '0.1'

from socket import inet_ntoa, inet_aton
from struct import pack, unpack

def dot_to_int(dotted_string):
    """Converts an IPv4 Internet address in dotted notation, 
    e.g. 127.0.0.1, to integer form, e.g. 2130706433.
    
    For example:
    
    >>> dot_to_int('127.0.0.1')
    2130706433
    """
    packed_binary = inet_aton(dotted_string)
    return unpack('!L', packed_binary)[0]

def int_to_dot(ip_integer):
    """Converts an IPv4 Internet address in integer form, 
    e.g. 2130706433, to dotted notation, e.g. 127.0.0.1.
    
    For example:
    
    >>> int_to_dot('2130706433')
    '127.0.0.1'
    """
    packed_long = pack('!L', long(ip_integer))
    return inet_ntoa(packed_long)

def ip_in_range(ip_address, from_address, to_address):
    """Tests whether the *ip_address* is between the 
    *from_address* and *to_address*.
    This function takes dotted notation for all inputs,
    as in the following examples:
    
    >>> ip_in_range('192.168.5.100', '192.168.0.1', '192.168.255.255')
    True
    >>> ip_in_range('127.0.0.1', '192.168.0.1', '192.168.255.255')
    False
    """
    iprange = xrange(dot_to_int(from_address), 
                     dot_to_int(to_address)) 
    if dot_to_int(ip_address) in iprange:
        return True
    else:
        return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()

