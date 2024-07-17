
using MyApp.Models;

namespace MyApp.Services
{
    public class GreetingService
    {
        public string Greet(Person person)
        {
            return $"Hello, {person.GetFullName()}!";
        }
    }
}
