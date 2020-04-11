# encoding: UTF-8
###########################3
#ubuntu查看穿透监管相关信息

from ctypes import *
libtest = cdll.LoadLibrary('/home/john/PYTHON/scripts/cta_machineInfo/LinuxDataCollect.so')

# testpy = libtest.CTP_GetSystemInfo
# testpy.argtype = c_char_p
# testpy.restype = c_int
# ss = "/systemInfo.sys"
# yy = 0
# params = testpy(ss,yy)
# print params

#_Z28CTP_GetSystemInfoUnAesEncodePcRi
#_Z17CTP_GetSystemInfoPcRi
#_Z21CTP_GetRealSystemInfoPcRi
func = getattr(libtest, '_Z21CTP_GetRealSystemInfoPcRi')
# func.argtypes = [c_char, c_int]
# func.restype = c_int
a=create_string_buffer(264)
b=c_int()
print (func(a, byref(b)))
print (a.value)
print (b)
# ret = chardet.detect(a.value)
# print(ret)

# print(a.value.encode('raw_unicode_escape'))
# print(a.value.encode('unicode_escape'))
# print(a.value.encode('utf-8'))
# print(a.value.encode('gbk'))
# print(a.value.encode('gb2312'))
