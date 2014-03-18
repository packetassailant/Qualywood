#!/usr/bin/python
# -*- coding: utf-8 -*-

# Qualywood was tested on OSX 10.8+
# ----------- OSX ---------------
# OSX: no deps
# ----------- Linux -------------
# Linux: no deps

from xml.etree.ElementTree import ElementTree
import csv
import getopt
import sys
import pickle as pk


def usage():
    print 'Info: Qualywood was created by Chris Patten'
    print 'Purpose: To parse Qualys xml'
    print 'Contact: cpatten[a.t.]packetresearch.com and @packetassailant\n'
    print 'Usage:  ./qualywood.py -i <qualys xml input file> -o <output file> -a'
    print '-a or --optiona        Parse xml format without IP/Network-Interface info'
    print '-b or --optionb        Parse xml format with IP/Network-Interface info'
    print '-h or --help           Print this help menu'
    print '-i or --infile         Qualys XML file (Required)'
    print '-o or --outfile        CSV output file name (Required)'


def parseQualysOne(infile):
    qualysType = 'a'
    hostname_list = []
    count_list = []
    qualys_list = []
    qualys_dict = {}
    et = ElementTree()
    et.parse(infile)
    qualys_list[:] = []
    qualys_dict.clear()
    for rootnode in et.getroot().getchildren():
        if rootnode.tag == 'data':
            for onenode in rootnode.getchildren():
                if onenode.tag == 'Asset':
                    hostname_list[:] = []
                    for twonode in onenode.getchildren():
                        if twonode.tag == 'id':
                            qualys_dict['id'] = twonode.text
                        if twonode.tag == 'name':
                            qualys_dict['name'] = twonode.text
                        if twonode.tag == 'hostName':
                            qualys_dict['hostName'] = twonode.text
                        for threenode in twonode.getchildren():
                            if threenode.tag == 'count' and '0' \
                                not in threenode.text:
                                qualys_dict['count'] = threenode.text
                            count_list[:] = []
                            for fournode in threenode.getchildren():
                                if fournode.tag == 'Tag':
                                    for fivenode in fournode.getchildren():
                                        if fivenode.tag == 'id':
                                            count_list.append(fivenode.text)
                                        if fivenode.tag == 'name':
                                            count_list.append(fivenode.text)
                            if count_list:
                                qualys_dict['instance'] = \
                                    '; '.join(count_list)
                                if 'hostName' not in qualys_dict:
                                    qualys_dict['hostName'] = 'None'
                                qualys_list.append(pk.dumps(qualys_dict))
    return qualys_list, qualysType


def parseQualysTwo(infile):
    qualysType = 'b'
    hostname_list = []
    qualys_list = []
    qualys_dict = {}
    et = ElementTree()
    et.parse(infile)
    qualys_list[:] = []
    qualys_dict.clear()
    for rootnode in et.getroot().getchildren():
        if rootnode.tag == 'data':
            for onenode in rootnode.getchildren():
                if onenode.tag == 'HostAsset':
                    hostname_list[:] = []
                    for twonode in onenode.getchildren():
                        if twonode.tag == 'id':
                            qualys_dict['id'] = twonode.text
                        if twonode.tag == 'name':
                            qualys_dict['name'] = twonode.text
                        if twonode.tag == 'nicAddresses':
                            for threenode in twonode.getchildren():
                                if threenode.tag == 'list':
                                    for fournode in threenode.getchildren():
                                        if fournode.tag == 'NetworkInterfaceAddress':
                                            for fivenode in fournode.getchildren():
                                                if fivenode.tag == 'inetAddress':
                                                    for sixnode in fivenode.getchildren():
                                                        if sixnode.tag == 'hostName':
                                                            qualys_dict['hostname'] = sixnode.text
                                                        if sixnode.tag == 'ipAddress':
                                                            qualys_dict['ipaddress'] = sixnode.text
                    qualys_list.append(pk.dumps(qualys_dict))                        
    return qualys_list, qualysType


def writecsv(list, outfile, qualysType):
    with open(outfile, 'w') as f:
        if qualysType == 'a':
            f.write('count,instances,hostname,id,name\n')
        if qualysType == 'b':
            f.write('hostname,ipaddress,id,name\n')
        for entry in list:
            dictentry = pk.loads(entry)
            w = csv.DictWriter(f, dictentry.keys())
            w.writerow(dictentry)
    f.close()


def main():
    found_a = False
    found_b = False
    found_i = False
    found_o = False
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'habi:o:', ['infile=',
                'outfile=', 'asset=', 'host='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if len(opts) == 0:
        usage()
        sys.exit(2)
    for (opt, arg) in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('-i', '--infile'):
            infile = open(arg, 'r')
            found_i = True
        elif opt in ('-o', '--outfile'):
            outfile = arg
            found_o = True
        elif opt in ('-a', '--optiona' ):
            found_a = True
        elif opt in ('-b', '--optionb'):
            found_b = True
        else:
            assert False, 'unhandled option'
    if found_i and not None and found_o and not None:
        if not found_a and not found_b:
            print  '-a or -b are mandatory arguments'
            usage()
            sys.exit(2)
        elif found_a and found_b:
            print  '-a and -b are mutually exclusive'
            usage()
            sys.exit(2)
        elif found_a and not found_b:
            qualys_list, qualyType = parseQualysOne(infile)
        elif found_b and not found_a:
            qualys_list, qualyType = parseQualysTwo(infile)
        else:
            print "Unknown Option"
            usage()
            sys.exit(2)
    else:
        print '-i and -o are mandatory arguments'
        usage()
        sys.exit(2)

    # Bootstrap

    writecsv(qualys_list, outfile, qualyType)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Caught KeyboardInterrupt, terminating execution'
        sys.exit(0)
