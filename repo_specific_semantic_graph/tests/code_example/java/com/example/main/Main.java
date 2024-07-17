package com.example.main;

import com.example.util.Greetings;  // Importing Greetings class
import com.example.models.User;     // Importing User class

public class Main {
    public static void main(String[] args) {
        User user = new User("John Doe");          // Using User class
        Greetings greetings = new Greetings();     // Using Greetings class

        System.out.println(greetings.getGreeting(user.getName()));  // Using methods from imported classes
    }
}
