from pathlib import Path
from textwrap import dedent

from dependency_graph.utils.tree_sitter_stub import (
    generate_java_stub,
    generate_c_sharp_stub,
    generate_ts_js_stub,
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
    print(actual)
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
    print(actual)

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
    print(actual)

    expected = dedent(
        """
        
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


def test_generate_typescript_stub_without_comments():
    code = dedent(
        """
        // Import the entire lodash library
        import _ from 'lodash';
        
        // Or, to import individual functions to potentially reduce bundle size
        import { shuffle, capitalize } from 'lodash';
        
        // Defining an interface
        interface Person {
          firstName: string;
          lastName: string;
        }
        
        // Implementing an interface with a class
        class Employee implements Person {
          constructor(public firstName: string, public lastName: string, public position: string) {}
        
          // Method
          introduceSelf(): void {
            console.log(`Hello, my name is ${this.firstName} ${this.lastName} and I am a ${this.position}.`);
          }
        }
        
        // Enum
        enum Status {
          Active,
          Inactive,
          Probation
        }
        
        // Function with return type
        function getStatusDescription(status: Status): string {
          switch (status) {
            case Status.Active:
              return 'The employee is active.';
            case Status.Inactive:
              return 'The employee is inactive.';
            case Status.Probation:
              return 'The employee is on probation.';
          }
        }
        
        // Generic function
        function getArrayItems<T>(items: T[]): T[] {
          return new Array<T>().concat(items);
        }
        
        // Arrow function with implicit return type
        const greet = (name: string): void => {
          console.log(`Hello, ${name}!`);
        };
        
        // Using the class and interface
        let emp: Person = new Employee("John", "Doe", "Developer");
        (emp as Employee).introduceSelf(); // Type assertion
        
        // Using the enum
        console.log(getStatusDescription(Status.Probation));
        
        // Using the generic function
        let numArray = getArrayItems<number>([1, 2, 3]);
        console.log(numArray);
        
        // Using the arrow function
        greet('Jane Doe');
        
        /* test
        * test
        */
        
        // Promise and async/await
        const promiseFunction = (): Promise<string> => {
          return new Promise<string>((resolve, reject) => {
            setTimeout(() => {
              resolve('Promise resolved!');
            }, 1000);
          });
        };
        
        const runAsyncCalls = async () => {
          console.log('Before promise execution');
          const result = await promiseFunction();
          console.log(result); // Output after 1 second: Promise resolved!
          console.log('After promise execution');
        };
        
        runAsyncCalls();
        
        const a = () => {console.log()}
        """
    )
    actual = generate_ts_js_stub(code, include_comments=False)
    print(actual)

    expected = dedent(
        """
        
        
        interface Person {
          firstName: string;
          lastName: string;
        }
        
        class Employee implements Person {
          constructor(public firstName: string, public lastName: string, public position: string)
        
          introduceSelf(): void
        }
        
        enum Status {
          Active,
          Inactive,
          Probation
        }
        
        function getStatusDescription(status: Status): string
        
        function getArrayItems<T>(items: T[]): T[]
        
        const greet = (name: string): void => {
          console.log(`Hello, ${name}!`);
        };
        
        let emp: Person = new Employee("John", "Doe", "Developer");
        (emp as Employee).introduceSelf();
        
        console.log(getStatusDescription(Status.Probation));
        
        let numArray = getArrayItems<number>([1, 2, 3]);
        console.log(numArray);
        
        greet('Jane Doe');
        
        
        const promiseFunction = (): Promise<string> => {
          return new Promise<string>((resolve, reject) => {
            setTimeout(() => {
              resolve('Promise resolved!');
            }, 1000);
          });
        };
        
        const runAsyncCalls = async () => {
          console.log('Before promise execution');
          const result = await promiseFunction();
          console.log(result);
          console.log('After promise execution');
        };
        
        runAsyncCalls();
        
        const a = () => {console.log()}"""
    )
    assert actual == expected
