class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower

    def display_info(self):
        return f"Engine with {self.horsepower} HP"


class Manufacturer:
    def __init__(self, name, country):
        self.name = name  # Manufacturer's name
        self.country = country  # Manufacturer's country

    def display_info(self):
        return f"{self.name} ({self.country})"
