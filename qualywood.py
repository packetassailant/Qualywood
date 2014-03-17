#!/usr/bin/python
# -*- coding: utf-8 -*-

# Qualywood was tested on OSX 10.8+
# ----------- OSX ---------------
# OSX: sudo easy_install pip
# OSX Deps: pip install -U -r environment.txt
# ----------- Linux -------------
# Linux: sudo apt-get install python-pip
# Linux Deps: pip install -U -r environment.txt

from xml.etree.ElementTree import ElementTree
import csv
import getopt
import sys
import pickle as pk

def usage():
    print 'Info: Qualywood was created by Chris Patten'
    print 'Purpose: To parse Qualys xml'
    print 'Contact: cpatten[a.t.]packetresearch.com and @packetassailant\n'
    print 'Usage:   ./qualywood.py -i <qualys xml input file> -o <output file>'
    print '-h or --help        Print this help menu'
    print '-i or --infile      Qualys XML file (Required)'
    print '-o or --outfile     XLS output file name (Required)'


def parseQualys(infile):
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
                            if threenode.tag == 'count' and '0' not in threenode.text:
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
                                qualys_dict["instance"] = '; '.join(count_list)
                                if 'hostName' not in qualys_dict:
                                    qualys_dict['hostName'] = 'None' 
                                qualys_list.append(pk.dumps(qualys_dict))
    return qualys_list

def writecsv(list, outfile):
    #write header
    with open(outfile, 'w') as f:
        f.write("count,instances,hostname,id,name\n")
        for entry in list:
            dictentry = pk.loads(entry)
            w = csv.DictWriter(f, dictentry.keys())
            w.writerow(dictentry)
    #write everything else    
    f.close() 


def main():
    found_i = False
    found_o = False
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], 'hi:o:', ['infile=',
                'outfile='])
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
        else:
            assert False, 'unhandled option'
    if found_i and not None and found_o and not None:
        qualys_list = parseQualys(infile)
    else:
        print '-i and -o are mandatory arguments'
        usage()
        sys.exit(2)

    # Bootstrap
    writecsv(qualys_list, outfile)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Caught KeyboardInterrupt, terminating execution'
        sys.exit(0)
