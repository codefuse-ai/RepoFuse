# Define the parent class
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass  # To be defined by the subclass


# Define the child class
class Dog(Animal):  # Inherits from the Animal class
    def speak(self):
        return "Woof!"


# Define another child class
class Cat(Animal):  # Inherits from the Animal class
    def speak(self):
        return "Meow!"


# Create instances of the child classes
my_dog = Dog("Buddy")
my_cat = Cat("Whiskers")
# Call the methods inherited from the parent class
print(my_dog.name)  # Output: Buddy
print(my_dog.speak())  # Output: Woof!
print(my_cat.name)  # Output: Whiskers
print(my_cat.speak())  # Output: Meow!
