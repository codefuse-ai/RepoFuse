package main

import (
    "fmt"
    "myproject/anotherpackage"
    "math/rand"            // Standard library package
    "time"                 // Another standard library package
    u "myproject/utils"    // Renamed import
    . "myproject/utils"    // Dot import
)

import "myproject/utils"

func main() {
    fmt.Println("Hello, World!")
    utils.PrintMessage()

    // Using the renamed import
    u.AnotherMessage()

    // Using the dot import
    PrintMessage()

    // Using a function from another package
    anotherpackage.AnotherFunction()

    // Using functions from standard library packages
    fmt.Println("Random number:", rand.Intn(100))
    fmt.Println("Current time:", time.Now())
}
