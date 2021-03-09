#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, getopt
from emass.emass import EMass

def main(argv):
    formula = argv[1]
    limit = 0
    charge = 0

    try:
        opts, args = getopt.getopt(argv[2:], "hl:c:")
    except getopt.GetoptError:
        print("demo.py -l <limit> -c <charge>")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print("demo.py -l <limit> -c <charge>")
            sys.exit()
        elif opt in ("-l"):
            limit = float(arg)
        elif opt in ("-c"):
            charge = int(arg)
    
    emass = EMass()
    result = emass.calculate(formula, limit=limit, charge=charge)
    print("formula:" + formula + " limit:" + str(limit) + " charge:" + str(charge))
    for p in result:
        print(p.mass, p.rel_area)

    sys.exit()

main(sys.argv)
