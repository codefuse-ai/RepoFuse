import networkx as nx

from dependency_graph.utils.digraph import lexicographical_cyclic_topological_sort


def test_lexicographical_cyclic_topological_sort():
    """
        2
      / \
     /   \
    1     5
    | \   |
    |  \  |
    3    4

    6 -> 7
    """
    DG = nx.DiGraph([(2, 1), (2, 5), (1, 3), (1, 4), (5, 4), (6, 7)])

    assert list(lexicographical_cyclic_topological_sort(DG)) == [2, 1, 3, 5, 4, 6, 7]


def test_lexicographical_cyclic_topological_sort1():
    """
    D ---> B
    ^    / ^
    |   /  |
    |  /   |
    | L    |
    A ---> C
    """
    DG = nx.DiGraph([("A", "C"), ("A", "D"), ("B", "A"), ("C", "B"), ("D", "B")])

    assert list(lexicographical_cyclic_topological_sort(DG)) == ["A", "C", "D", "B"]


def test_lexicographical_cyclic_topological_sort2():
    DG = nx.DiGraph()
    DG.add_node("A")
    DG.add_node("B")

    assert list(lexicographical_cyclic_topological_sort(DG)) == ["A", "B"]


def test_lexicographical_cyclic_topological_sort3():
    """
    A -> B
    ^    |
    |    v
    D <- C
    """
    DG = nx.DiGraph([("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")])

    assert list(lexicographical_cyclic_topological_sort(DG)) == ["A", "B", "C", "D"]


def test_lexicographical_cyclic_topological_sort4():
    """
        2
      / \
     /   \
    1     5
    | \   |
    |  \  |
    3    4
    """
    DG = nx.DiGraph([(2, 1), (2, 5), (1, 3), (1, 4), (5, 4)])

    assert list(lexicographical_cyclic_topological_sort(DG)) == [2, 1, 3, 5, 4]
    assert list(lexicographical_cyclic_topological_sort(DG, key=lambda x: -x)) == [
        2,
        5,
        1,
        4,
        3,
    ]


def test_lexicographical_cyclic_topological_sort5():
    DG = nx.DiGraph([(1, "red"), (3, "red"), (1, "green"), (2, "blue")])

    key = lambda node: (isinstance(node, str), node)
    assert list(lexicographical_cyclic_topological_sort(DG, key=key)) == [
        1,
        2,
        3,
        "blue",
        "green",
        "red",
    ]


def test_lexicographical_cyclic_topological_sort6():
    """
    Self-referencing nodes
    +---+
    | 1 |
    +---+
    ^ |
    | |
    +-+
    """
    DG = nx.DiGraph([(1, 1)])

    key = lambda node: (isinstance(node, str), node)
    assert list(lexicographical_cyclic_topological_sort(DG, key=key)) == [1]
