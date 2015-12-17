#!/usr/bin/python

from argparse import ArgumentParser
from math import log10
from itertools import combinations
import codecs, sys, re

parser = ArgumentParser()
parser.add_argument('dicts', nargs='+', help='csv wordlists to read')
parser.add_argument('-w','--weight', nargs='+', help='relative weights for various wordlists')
parser.add_argument('-o','--output', help='Output file')
parser.add_argument('-m','--min', help='Minimum codepoint value accepted')
args = parser.parse_args()

def checkok(t, w) :
    if args.min is None : return True
    if t.endswith(u"\u17d2") : return False
    if not all(map(lambda x: args.min <= ord(x) < args.min + 256, t)) : return False
    if any(map(lambda x: 0x17e0 <= ord(x) < 0x17ea, t)) : return False
    return True

if args.output :
    outfh = codecs.open(args.output, 'w', 'utf-8')
else :
    outfh = codecs.getwriter('utf-8')(sys.stdout)

args.min = int(args.min, base=0)
d = {}
total = 0.
m = None
for i in range(len(args.dicts)) :
    fh = codecs.open(args.dicts[i], 'r', 'utf-8')
    ft = 0.
    for l in fh.readlines() :
        t = l.strip().replace(u'\u200B', '')
        if t.startswith(u'\ufeff') : t = t[1:]
        if t.startswith('#') : continue
        c = t.find(",")
        if c < 0 : c = t.find("\t")
        if c > 0 :
            w = float(t[c+1:])
            t = t[0:c].rstrip()
        else :
            w = 1
        w *= (args.weight[i] if args.weight is not None and i < len(args.weight) else 1.)
        if checkok(t, w) :
            d[t] = w
            ft += w
            m = min(m, w) if m is not None else w
    fh.close()
    total += ft
    if args.output :
        print "Total for {} = {:f}".format(args.dicts[i], ft)

equivs = [
    (re.compile(ur'(\u17d2[\u178a\u178f])'), 1, 5),
    (re.compile(ur'(\u17d2[\u178b\u1792])'), 1, 0x19),
    (re.compile(ur'([\u17b7\u17b8])'), 0, 1),
    (re.compile(ur'([\u17b1\u17b3])'), 0, 2),
    (re.compile(ur'\u17cc'), 0, 3),
    (re.compile(ur'\u17cf'), 0, 2),
]

def acsum2(x) :
    a = x[0]
    yield a
    for i in range((len(x)-2)/2) :
        a += x[i*2 + 1]
        a += x[i*2 + 2]
        yield a

def procequiv(a, d, extras) :
    for e in equivs :
        if not isinstance(a, basestring) :
            if e[0] in a[1] : continue
            k = a[0]
        else :
            k = a
        s = re.split(e[0], k)
        if len(s) == 1 : continue
        inds = list(acsum2(map(len, s)))
        for i in range(len(inds)) :
            for c in combinations(inds, i+1) :
                t = list(k)
                for j in c :
                    t[j+e[1]] = unichr(ord(t[j+e[1]]) ^ e[2])
                    r = u"".join(t)
                    d[r] = d[k]
                    if not isinstance(a, basestring) :
                        extras.append((r, a[1] + [e[0]]))
                    else :
                        extras.append((r, [e[0]]))

extras = []
for k in d.keys() :
    procequiv(k, d, extras)
for k in extras :
    procequiv(k, d, extras)

scale = 255. / log10(m/total)

outfh.write(u"\ufeff# Combined dictionary from:\n#   " + u"\n#   ".join(args.dicts) + u"\n")
for k in sorted(d.keys()) :
    if len(k) == 0 : continue
    outfh.write(u"{}\t{}\n".format(k, int(log10(d[k] / total) * scale)))
outfh.close()
            
