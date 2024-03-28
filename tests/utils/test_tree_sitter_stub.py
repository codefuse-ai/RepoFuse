from textwrap import dedent

from dependency_graph.utils.tree_sitter_stub import generate_java_stub


def test_generate_java_stub():
    code = dedent(
        """
        import java.io.*;
        /**
         * Block comment
         */
        public class Test {
            // line comment
            private int X;
            public int Y;
            
            public Test() {
                System.out.println("Hello, world!");
            }
        
            public void test() {
                System.out.println("Hello, world!");
            }
            
            public static void main(String[] args) {
                System.out.println("Hello, world!");
            }
        }
        """
    )
    actual = generate_java_stub(code)
    expected = dedent(
        """
        
        /**
         * Block comment
         */
        public class Test {
            // line comment
            private int X;
            public int Y;
            
            public Test()
        
            public void test()
            
            public static void main(String[] args)
        }"""
    )
    assert actual == expected


def test_generate_java_stub_without_comments():
    code = dedent(
        """
        import java.io.*;
        /**
         * Block comment
         */
        public class Test {
            // line comment
            private int X;
            public int Y;

            public Test() {
                System.out.println("Hello, world!");
            }

            public void test() {
                System.out.println("Hello, world!");
            }

            public static void main(String[] args) {
                System.out.println("Hello, world!");
            }
        }
        """
    )
    actual = generate_java_stub(code, include_comments=False)
    expected = dedent(
        """


        public class Test {
        
            private int X;
            public int Y;

            public Test()

            public void test()

            public static void main(String[] args)
        }"""
    )
    assert actual == expected
