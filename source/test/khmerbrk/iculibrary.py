#!/usr/bin/python

from ctypes import *
import os, codecs

c_int_p = POINTER(c_int)
c_uint_p = POINTER(c_uint)
c_uint16_p = POINTER(c_uint16)
c_int32_p = POINTER(c_uint16)

class UParseError(Structure) :
    _fields_ = [('line', c_int32),
                ('offset', c_int32),
                ('preContext', c_void_p),
                ('postContext', c_void_p)]

class IcuLibrary:
    def __init__(self, icuFilePath, icuVersion):
        self.icuFilePath = icuFilePath
        self.icuVersion = icuVersion
        self.iculib = cdll.LoadLibrary(os.path.join(self.icuFilePath, 'libicuuc.so.' + str(self.icuVersion)))
        self.fn('ubrk_open', c_void_p,  c_int, c_char_p, c_void_p, c_int32, c_int_p)
        self.fn('u_strFromUTF8', c_void_p, c_uint16_p, c_int32, c_int32_p, c_char_p, c_int32, c_int_p)
        self.fn('ubrk_first', c_int32, c_void_p)
        self.fn('ubrk_next', c_int32, c_void_p)
        self.fn('ubrk_setText', None, c_void_p, c_void_p, c_uint32, c_int_p)
        self.fn('uset_openPattern', c_void_p, c_void_p, c_int32, c_int_p)
        self.fn('uset_contains', c_int8, c_void_p, c_uint32)

        self.fn('ubrk_openRules', c_void_p, c_void_p, c_int32, c_void_p, c_int32, POINTER(UParseError), c_int_p)
        self.fn('ubrk_close', None, c_void_p)

    def fn(self, name, res, *params) :
        f = getattr(self.iculib, name + '_' + str(self.icuVersion))
        f.restype = res
        f.argtypes = params
    
    def icucall(self, name, *params) :
        f = getattr(self.iculib, name + '_' + str(self.icuVersion))
        return f(*params)

    def status(self):
        return c_int();
    
    def uchars(self, s) :
        t = codecs.encode(s, 'utf_16_le')
        res = create_string_buffer(t, len(t) + 2)
        return t
        status = c_int()
        nchar = c_uint(len(s))
        self.icucall('u_strFromUTF8', c_uint16_p(res), nchar, c_uint_p(c_uint(0)), t, len(t), byref(status))
        return res

class rbbi(object) :
    def __init__(self, iculib, rules='', locale='') :
        self.iculib = iculib
        self.status = c_int()
        if len(rules) :
            self.pError = UParseError()
            self.ruleschars = self.iculib.uchars(rules)
            self.brk = self.iculib.icucall('ubrk_openRules', self.ruleschars, len(rules), '', 0, self.pError, byref(self.status))
        else :
            self.brk = self.iculib.icucall('ubrk_open', 2, locale, '', 0, byref(self.status))
            self.ruleschars = None
            self.pError = None

    def __del__(self) :
        self.iculib.icucall('ubrk_close', self.brk)
        del self.ruleschars
        del self.pError

    def error_report(self) :
        if self.status.value != 0 :
            if self.ruleschars is not None :
                return "Failed to load rules: status = {}, at {}:{}".format(self.status.value, self.pError.line, self.pError.offset)
            else :
                return "Failed to load breaker: status = {}".format(self.status.value)
