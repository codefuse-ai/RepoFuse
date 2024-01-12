import os


class A:
    var_a = 1
    def a(self):
        self.var_a = 1
        print("in A.a()")


def func():
    def closure():
        print("in closure")

    closure()


global_var = 1

global_var += 1

os.cpu_count()
func()
A().a()
print(A().a())
