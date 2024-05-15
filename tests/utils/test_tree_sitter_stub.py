from textwrap import dedent

from dependency_graph.utils.tree_sitter_stub import (
    generate_java_stub,
    generate_c_sharp_stub,
)


def test_generate_java_stub():
    code = dedent(
        """
        import java.io.*;
        /**
         * Block comment
         */
        public class Test {
            // line comment
            private int X;
            public int Y;
            
            public Test() {
                System.out.println("Hello, world!");
            }
        
            public void test() {
                System.out.println("Hello, world!");
            }
            
            public static void main(String[] args) {
                System.out.println("Hello, world!");
            }
        }
        """
    )
    actual = generate_java_stub(code)
    expected = dedent(
        """
        
        /**
         * Block comment
         */
        public class Test {
            // line comment
            private int X;
            public int Y;
            
            public Test()
        
            public void test()
            
            public static void main(String[] args)
        }"""
    )
    assert actual == expected


def test_generate_java_stub_without_comments():
    code = dedent(
        """
        import java.io.*;
        /**
         * Block comment
         */
        public class Test {
            // line comment
            private int X;
            public int Y;

            public Test() {
                System.out.println("Hello, world!");
            }

            public void test() {
                System.out.println("Hello, world!");
            }

            public static void main(String[] args) {
                System.out.println("Hello, world!");
            }
        }
        """
    )
    actual = generate_java_stub(code, include_comments=False)
    expected = dedent(
        """


        public class Test {
        
            private int X;
            public int Y;

            public Test()

            public void test()

            public static void main(String[] args)
        }"""
    )
    assert actual == expected


def test_generate_c_sharp_stub_without_comments():
    code = dedent(
        """
        using System;
        using System.Collections.Generic;
        using System.Linq;
        using System.Threading.Tasks;
        
        // Define an enum
        public enum ComputerType
        {
            Laptop,
            Desktop,
            Tablet
        }
        
        // Define an interface
        public interface IComputer
        {
            ComputerType Type { get; }
            void TurnOn();
        }
        
        // Base class
        public abstract class Computer : IComputer
        {
            public ComputerType Type { get; private set; }
            public string Name { get; protected set; }
            
            public Computer(ComputerType type)
            {
                Type = type;
            }
        
            public virtual void TurnOn()
            {
                Console.WriteLine($"{Name} is turning on.");
            }
        }
        
        // Derived class with polymorphism and overriding
        public class Laptop : Computer
        {
            public Laptop() : base(ComputerType.Laptop)
            {
                Name = "Laptop";
            }
        
            public override void TurnOn()
            {
                // Base implementation call
                base.TurnOn();
                Console.WriteLine("Welcome to your laptop.");
            }
        }
        
        // Generic class
        public class Inventory<T>
        {
            private List<T> _items = new List<T>();
        
            public void Add(T item)
            {
                _items.Add(item);
            }
        
            // Generic method
            public T FindFirst()
            {
                return _items.First();
            }
        }
        
        // Event
        public class Button
        {
            // Define event delegate
            public event Action OnClick;
        
            // Method to raise the event
            public void Click()
            {
                OnClick?.Invoke();
            }
        }
        
        class Program
        {
            static async Task Main(string[] args)
            {
                // Use of enum and polymorphism
                IComputer myLaptop = new Laptop();
                myLaptop.TurnOn(); // Polymorphic call
        
                // Generics
                Inventory<IComputer> inventory = new Inventory<IComputer>();
                inventory.Add(myLaptop);
                var firstItem = inventory.FindFirst();
        
                // Lambda expression and LINQ
                List<int> numbers = new List<int> { 1, 2, 3, 4, 5 };
                var evenNumbers = numbers.Where(n => n % 2 == 0).ToList();
                evenNumbers.ForEach(n => Console.WriteLine(n));
        
                // Event subscription with lambda expression
                Button button = new Button();
                button.OnClick += () => Console.WriteLine("Button was clicked!");
        
                // Raising an event
                button.Click();
        
                // Exception handling
                try
                {
                    // Simulate an error
                    throw new InvalidOperationException("Something went wrong.");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error: {ex.Message}");
                }
        
                // Asynchronous programming with async and await
                string result = await SimulateDataProcessing();
                Console.WriteLine(result);
            }
        
            // Asynchronous method
            public static async Task<string> SimulateDataProcessing()
            {
                await Task.Delay(1000); // Simulate a task taking 1 second
                return "Data processed asynchronously.";
            }
        }
        """
    )
    actual = generate_c_sharp_stub(code, include_comments=False)
    expected = dedent(
        """\
        






        public enum ComputerType
        {
            Laptop,
            Desktop,
            Tablet
        }
        
        
        public interface IComputer
        {
            ComputerType Type
            void TurnOn();
        }
        
        
        public abstract class Computer : IComputer
        {
            public ComputerType Type
            public string Name
        
            public Computer(ComputerType type)
        
        
            public virtual void TurnOn()
        
        }
        
        
        public class Laptop : Computer
        {
            public Laptop() : base(ComputerType.Laptop)
        
        
            public override void TurnOn()
        
        }
        
        
        public class Inventory<T>
        {
            private List<T> _items = new List<T>();
        
            public void Add(T item)
        
        
        
            public T FindFirst()
        
        }
        
        
        public class Button
        {
        
            public event Action OnClick;
        
        
            public void Click()
        
        }
        
        class Program
        {
            static async Task Main(string[] args)
        
        
        
            public static async Task<string> SimulateDataProcessing()
        
        }"""
    )
    assert actual == expected
