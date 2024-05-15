import enum


class Language(str, enum.Enum):
    CSharp = "c_sharp"
    Python = "python"
    Java = "java"
    JavaScript = "javascript"
    TypeScript = "typescript"

    def __str__(self):
        return self.value
