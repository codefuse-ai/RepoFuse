package com.example

import com.example.subpackage.* // Wildcard import

fun main() {
    println("Using wildcard imports:")
    val utility = Utility()
    utility.printMessage()
}
