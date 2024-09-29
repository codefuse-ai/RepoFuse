from .base_class import Animal


class Dog(Animal):
    def speak(self):
        return "Dog barks"


class Cat(Animal):
    def speak(self):
        return "Cat meows"


class Lion(Cat):
    def speak(self):
        return "Lion roars"


# Create instances of Dog and Cat
dog = Dog()
cat = Cat()
lion = Lion()

# Call the speak method from each instance
print(dog.speak())  # Output: Dog barks
print(cat.speak())  # Output: Cat meows
print(lion.speak())  # Output: Lion roars

# Call the speak method from the Animal class
animal = Animal()
print(animal.speak())  # Output: Animal speaks
