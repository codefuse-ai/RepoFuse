# Define the first parent class
class Father:
    def __init__(self):
        self.father_name = "Doe"

    def show_father(self):
        print("Father:", self.father_name)


# Define the second parent class
class Mother:
    def __init__(self):
        self.mother_name = "Jane"

    def show_mother(self):
        print("Mother:", self.mother_name)


# Define the child class inheriting from Father and Mother
class Child(Father, Mother):
    def __init__(self):
        # Call __init__ on both parents
        Father.__init__(self)
        Mother.__init__(self)

    def show_parent(self):
        print("Father:", self.father_name)
        print("Mother:", self.mother_name)


# Create an instance of the Child class
my_child = Child()
my_child.show_parent()
