// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "MySwiftProject",
    products: [
        .executable(name: "MyApp", targets: ["MyApp"]),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "MyApp",
            dependencies: ["Utilities", "Other"]
        ),
        .target(
            name: "Utilities",
            dependencies: []
        ),
        .target(
            name: "Other",
            dependencies: []
        ),
        .testTarget(
            name: "MyAppTests",
            dependencies: ["MyApp"]
        ),
    ]
)
