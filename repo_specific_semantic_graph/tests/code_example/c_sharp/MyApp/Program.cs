
using System;
using MyApp.Models;
using MyApp.Services;
using MyLibrary;

namespace MyApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");

            var person = new Person { FirstName = "John", LastName = "Doe" };
            Console.WriteLine(person.GetFullName());

            var greetingService = new GreetingService();
            Console.WriteLine(greetingService.Greet(person));

            Console.WriteLine(MathLibrary.Add(5, 3));
        }
    }
}
