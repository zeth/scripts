#!/usr/bin/env python
"""Infomation about wireless connections mananged by Network Manager.""" 
import gconf

LOCATION = "/system/networking/wireless/networks"

class Connection(object):
    """A wireless connection."""

    def __init__(self, path):
        self.path = path 
        self.name = gconfname(path)

    def __str__(self):
        return self.name

    def info(self):
        """Print Info about wireless networks.
        Not yet implemented."""
        pass

    def delete(self):
        """Delete information about a connection from the system.
        Not yet implemented."""
        pass

    def time(self):
        """Return the connection time as a datetime object."""
        import datetime
        return datetime.datetime.fromtimestamp(self.timestamp)

class Network(object):
    """All the networks you have ever visited."""
    def __init__(self):
        client = gconf.Client()
        for i in client.all_dirs(LOCATION): 
            myconnection = Connection(i)
            for j in client.all_entries(i):
                setattr(myconnection, 
                        gconfname(j.get_key()),
                        extract_value(j.get_value()))
                setattr(self, 
                        gconfname(i), 
                        myconnection)

    def __str__(self):
        connections = ""
        for i in self.__dict__:
            connections += str(i) + "\n"
        return connections

def extract_value(gconfvalue):
    """Convert GConfValue into simple Python object."""
    k = gconfvalue.type.value_nick
    if k == 'int':
        value = gconfvalue.get_int()
    elif k == 'string':
        value = gconfvalue.get_string()
    elif k == 'list':
        value = []
        for j in gconfvalue.get_list():
            value.append(extract_value(j))
    return value

def gconfname(path):
    """Turn gconf path into name."""
    return path.split('/')[-1]


def main():
    """Print out list of connections."""
    networks = Network()
    print "\nYou have accessed the following wireless networks:\n"
    print "Name", " " * 11, "Added\n"
    for i in networks.__dict__:
        indent = " " * (15 - len(str(networks.__dict__[i].name)))
        print networks.__dict__[i].name, indent, networks.__dict__[i].time()

# start the ball rolling
if __name__ == "__main__":
    main()
