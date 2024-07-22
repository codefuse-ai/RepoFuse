package com.example

import com.example.subpackage.Utility // Absolute import

fun main() {
    println("Using absolute imports:")
    val utility = Utility()
    utility.printMessage()
}
