import enum


class Language(str, enum.Enum):
    CSharp = "c-sharp"
    Python = "python"
    Java = "java"
    JavaScript = "javascript"
    TypeScript = "typescript"
