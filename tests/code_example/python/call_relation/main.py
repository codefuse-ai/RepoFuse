from x import func_x


class A:
    def a(self):
        print("in A.a()")

    def b(self):
        def closure():
            print("in A.b()")
            self.a()

        closure()


def func():
    A().a()
    func_x()


global_var_1 = A().b()
global_var_2 = func()

if __name__ == "__main__":
    A().b()
    func()
