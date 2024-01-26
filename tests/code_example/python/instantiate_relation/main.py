from x import X


class A:
    def __init__(self, a):
        self.a = a


class B:
    def __init__(self, b):
        self.b = b

    def return_A(self):
        class_a = A(self.b)
        x = X()
        return class_a


def func_1():
    class_a = A(1)
    x = X()
    return class_a


global_class_a = A(2)


def func_2(class_a):
    class_a.a += 1
    B(2)
    A_in_func_2 = B(3).return_A()
    return A_in_func_2


func_2(global_class_a)

B(3).return_A()


from x import X

class_x = X()
