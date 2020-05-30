import sys
a = 1
for i in range(10):
    pass


def outer_func(g=3):
    loc_var = "local variable"

    def inner_func():
        print(a)
        print(g)

        try:
            int("0.2")
        except ValueError as e:
            print(e)

        loc_var += " in inner func"
        return loc_var

    return inner_func


clo_func = outer_func()
clo_func()


class clss():
    def add(self):
        pass

#
# def outer_func(out_flag):
#     if out_flag:
#         loc_var1 = 'local variable with flag'
#     else:
#         loc_var2 = 'local variable without flag'
#
#     def inner_func(in_flag):
#         return loc_var1 if in_flag else loc_var2
#
#     return inner_func
#
#
# clo_func = outer_func(True)
# print(clo_func(False))
