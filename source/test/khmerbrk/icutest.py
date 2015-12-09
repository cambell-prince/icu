#!/usr/bin/python

from iculibrary import IcuLibrary, rbbi
from ctypes import byref

from argparse import ArgumentParser
import codecs, sys

p = ArgumentParser()
p.add_argument('infile', help='Input text file to process')
p.add_argument('-o','--output', help='Output file for results')
p.add_argument('-u','--icuVersion', type = int, required = True, help='ICU Version number')
p.add_argument('-d','--icuDir', default = '', help='Directory of ICU library, else path')
p.add_argument('-r','--rules', help = 'File containing break iteration rules')
p.add_argument('-l','--locale', default = '', help = 'Locale to use for break iterator')
p.add_argument('-c','--rangeCheck', help = 'Character block to do range checking on')
args = p.parse_args()

iculib = IcuLibrary(args.icuDir, args.icuVersion)

if args.output :
    outf = codecs.open(args.output, 'w', 'utf-8')
else :
    outf = codecs.getwriter('UTF-8')(sys.stdout)
inf = codecs.open(args.infile, 'r', 'utf-8')

status = iculib.status()
if args.rules :
    fh = codecs.open(args.rules, 'r', 'utf-8')
    rules = fh.read()
    fh.close
    brk = rbbi(rules = rules)
else :
    brk = rbbi(locale = args.locale)
#if brk.status.value != 0 :
#    print brk.error_report()
#    del brk
#    sys.exit(1)

if args.rangeCheck is not None :
    addedbreaks = 0
    totalbreaks = 0
    pattern = "[[:" + args.rangeCheck + ":]&[:LineBreak=SA:]]"
    checkSet = iculib.icucall('uset_openPattern', iculib.uchars(pattern), len(pattern), status)
    if status.value != 0 :
        checkSet = None
else :
    checkSet = None

ntext = ''
for l in inf.readlines() :
    text = iculib.uchars(l)
    iculib.icucall('ubrk_setText', brk.brk, text, len(l), byref(status))
    ntext = text
    res = ''
    curr = 0
    while curr != -1 :
        prev = curr
        curr = iculib.icucall('ubrk_next', brk.brk)
        if curr != -1 :
            if checkSet is not None :
                if curr < len(l) - 1 and iculib.icucall('uset_contains', checkSet, ord(l[curr - 1])) and \
                   iculib.icucall('uset_contains', checkSet, ord(l[curr])) :
                    addedbreaks += 1
                    res = res + l[prev:curr] + '|'
                else :
                    res = res + l[prev:curr]
                totalbreaks += 1
            else:
                res = res + l[prev:curr] + '|'
        else :
            res = res + l[prev:]
    outf.write(res)
inf.close()
if args.output :
    outf.close()
if checkSet is not None :
    print "Added {} breaks of {} total breaks".format(addedbreaks, totalbreaks)
del brk
