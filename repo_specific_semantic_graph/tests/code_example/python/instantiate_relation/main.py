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

if class_x:
    global_class_b = A(4)
else:
    global_class_b = B(5)


def func_3(class_a_or_b):
    print(class_a_or_b)


func_3(A(4))
func_3(B(5))
