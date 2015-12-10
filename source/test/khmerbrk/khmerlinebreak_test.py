# coding=utf-8

import unittest

from iculibrary import IcuLibrary, rbbi
from ctypes import byref
import os

class TestKhmerBreaking(unittest.TestCase):
    def setUp(self):
        self.icu56 = IcuLibrary(os.path.join(os.path.dirname(__file__), '../../lib'), '56')
        self.rbbi56 = rbbi(self.icu56, locale='km_KH')
        self.icu52 = IcuLibrary('/usr/lib/x86_64-linux-gnu', '52')
        self.rbbi52 = rbbi(self.icu52, locale='km_KH')
    
    def break56(self, l):
        status = self.icu56.status()
        text = self.icu56.uchars(l)
        self.icu56.icucall('ubrk_setText', self.rbbi56.brk, text, len(l), byref(status))
#         ntext = text
        res = ''
        curr = 0
        while curr != -1 :
            prev = curr
            curr = self.icu56.icucall('ubrk_next', self.rbbi56.brk)
            if curr != -1 :
#                 if checkSet is not None :
#                     if curr < len(l) - 1 and self.icu56.icucall('uset_contains', checkSet, ord(l[curr - 1])) and \
#                        self.icu56.icucall('uset_contains', checkSet, ord(l[curr])) :
#                         addedbreaks += 1
#                         res = res + l[prev:curr] + '|'
#                     else :
#                         res = res + l[prev:curr]
#                     totalbreaks += 1
#                 else:
                res = res + l[prev:curr] + '|'
            else :
                res = res + l[prev:]
#        print res
        #outf.write(res)
        return res;

    def doTest(self, t) :
        self.maxDiff = None
	s = t.replace(u"|", "")
        result = self.break56(s)
        self.assertEqual(t, result)
        assert True == True, 'not really'
    
    def testOne(self):
        s = u'រដ្ឋមន្ត្រី​|ក្រសួង​|ការបរទេស​|កម្ពុជា​|ដែល​|រង​|ការ​|ចោទថា |ជា​|អតីត​|មេ​|គុក​|បឹងត្របែក​|សម័យ​|ខ្មែរក្រហម |អំពាវនាវ​|ឱ្យ​|អាជ្ញា​|ធរមាន​|សមត្ថកិច្ច​|អនុវត្ត​|សាលដីកា |តាម​|ចាប់ខ្លួន​|មេដឹកនាំ​|គណបក្សប្រឆាំង​|ដែល​|កំពុង​|គេចខ្លួន​|នៅ​|ក្រៅប្រទេស​|។​|'
        self.doTest(s)

    def testTwo(self):
        s = u'ថ្លែង|បែបនេះ|នៅក្នុង|កម្មវិធី|ជួបជុំ|ជាមួយ|តំណាង|យុវជន|មក|ពី|២៥|រាជធានី|ខេត្ត|ប្រមាណជា​|'
        self.doTest(s)

    def testThree(self):
        self.doTest(u'នទ្រែល​|មា​|យោហាន|')

    def testFour(self):
        self.doTest(u'​|យេរូឆាលឹម​| |')

if __name__ == '__main__' :
    unittest.main()

