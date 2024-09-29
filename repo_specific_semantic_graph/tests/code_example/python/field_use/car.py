from .engine import Engine, Manufacturer


class Car:
    # Class member (attribute) initialized outside __init__
    manufacturer_info = None  # Class variable to hold manufacturer info

    def __init__(self, make, model, year, engine):
        # Initialize fields for the Car class
        self.make = make
        self.model = model
        self.year = year
        self.engine = engine

    @classmethod
    def set_manufacturer(cls, name, country):
        cls.manufacturer_info = Manufacturer(name, country)

    def display_info(self):
        # Method to display the car's information along with engine and manufacturer info
        manufacturer = (
            self.manufacturer_info.display_info()
            if self.manufacturer_info
            else "Unknown Manufacturer"
        )
        return f"{self.year} {self.make} {self.model} - {self.engine.display_info()} - {manufacturer}"


# Create an instance of the Engine class
my_engine = Engine(horsepower=300)

# Set manufacturer information using the class method
Car.set_manufacturer("Toyota", "Japan")

# Create an instance of the Car class
my_car = Car("Toyota", "Camry", 2020, my_engine)

# Call the method to display car information
print(
    my_car.display_info()
)  # Output: 2020 Toyota Camry - Engine with 300 HP - Toyota (Japan)
