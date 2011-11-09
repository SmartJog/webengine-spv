#!/usr/bin/python

from importer import Importer
from pprint import pprint

def main():
    """ Initialize dev DB. """

    imp = Importer()
    imp['distant_url'] = 'https://spvrxtxws-dev-1.core/exporter/'

    # Create groups
    ret = imp.call('spv.services', 'create_groups', ['rxtxs-dev'])
    grp_id = ret.keys()[0]

    # Create objects
    dev_machines = []
    for idx in range(1, 9):
        dev_machines.append({'address': 'sj-dev-%d' % idx, 'group_id': grp_id})

    ret = imp.call('spv.services', 'create_objects', dev_machines)
    pprint(ret)


if __name__ == '__main__':
    main()
