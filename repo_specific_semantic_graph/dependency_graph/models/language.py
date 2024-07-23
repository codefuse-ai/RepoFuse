import enum


class Language(str, enum.Enum):
    CSharp = "c_sharp"
    Python = "python"
    Java = "java"
    Kotlin = "kotlin"
    JavaScript = "javascript"
    TypeScript = "typescript"
    PHP = "php"

    def __str__(self):
        return self.value
