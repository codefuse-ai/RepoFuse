from b import func_b


def func_a():
    print("In func_a")
    func_b()


# Trigger the chain of calls
if __name__ == "__main__":
    func_a()
