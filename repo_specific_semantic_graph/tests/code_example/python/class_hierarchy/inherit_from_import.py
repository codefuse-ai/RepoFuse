from .single_inheritance import Animal


class Cow(Animal):  # Inherits from the Animal class
    def speak(self):
        return "Moo!"
