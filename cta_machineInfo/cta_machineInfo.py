# encoding: UTF-8
###########################3
#ubuntu查看穿透监管相关信息

import os
from ctypes import *

file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'LinuxDataCollect.so')
libtest = cdll.LoadLibrary(file_path)
# '_Z28CTP_GetSystemInfoUnAesEncodePcRi', '_Z17CTP_GetSystemInfoPcRi',
func_str = '_Z21CTP_GetRealSystemInfoPcRi'
func = getattr(libtest, func_str)
a = create_string_buffer(264)
b = c_int()
print('func_str %s' % func_str)
print(func(a, byref(b)))
print(a.value)
print(b)
