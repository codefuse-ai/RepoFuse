class A:
    def __init__(self, a):
        self.a = a


class B:
    def __init__(self, b):
        self.b = b

    def return_A(self):
        class_a = A(self.b)
        return class_a


def func_1():
    class_a = A(1)
    return class_a


class_a = A(2)


def func_2(class_a):
    class_a.a += 1
    B(2)
    B(3).return_A()
    return class_a


func_2(class_a)

B(3).return_A()
