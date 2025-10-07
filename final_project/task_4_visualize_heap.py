"""
Візуалізація бінарної купи як дерева.

Ідея:
- Маємо масив `heap`, що представляє бінарну купу (мін- або макс-купу).
- Індексування: для вузла i -> лівий дит. = 2*i+1, правий дит. = 2*i+2.
- Будуємо дерево із вузлів Node і використовуємо NetworkX + Matplotlib для відображення.

Функції:
- heap_array_to_tree(heap, kind='min', color_ok='skyblue', color_bad='salmon'):
    Створює дерево з масиву купи. Кольорує вузли, що порушують властивість купи.
- visualize_heap(heap, kind='min'):
    Готує дерево та викликає малювання.

Примітка:
- Код використовує NetworkX і Matplotlib. Переконайтесь, що пакети встановлені:
    pip install networkx matplotlib
"""

import uuid
import math
from typing import List, Optional, Tuple

import networkx as nx
import matplotlib.pyplot as plt


class Node:
    def __init__(self, key, color="skyblue"):
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        self.val = key
        self.color = color   # Колір вузла
        self.id = str(uuid.uuid4())  # Унікальний ідентифікатор для вузла


def add_edges(graph: nx.DiGraph, node: Optional[Node], pos: dict, x: float = 0, y: float = 0, layer: int = 1) -> nx.DiGraph:
    """
    Рекурсивно додає вершини та ребра у граф для відображення дерева.
    Вузли розкладаються по шарах (layer) з горизонтальним зсувом 1/(2^layer).
    """
    if node is not None:
        graph.add_node(node.id, color=node.color, label=node.val)  # Вузол з id, кольором та міткою (значенням)
        if node.left:
            graph.add_edge(node.id, node.left.id)
            l = x - 1 / 2 ** layer
            pos[node.left.id] = (l, y - 1)
            add_edges(graph, node.left, pos, x=l, y=y - 1, layer=layer + 1)
        if node.right:
            graph.add_edge(node.id, node.right.id)
            r = x + 1 / 2 ** layer
            pos[node.right.id] = (r, y - 1)
            add_edges(graph, node.right, pos, x=r, y=y - 1, layer=layer + 1)
    return graph


def draw_tree(tree_root: Node) -> None:
    """Малює дерево, використовуючи NetworkX та задані позиції вузлів."""
    tree = nx.DiGraph()
    pos = {tree_root.id: (0, 0)}
    tree = add_edges(tree, tree_root, pos)

    colors = [node[1]["color"] for node in tree.nodes(data=True)]
    labels = {node[0]: node[1]["label"] for node in tree.nodes(data=True)}

    plt.figure(figsize=(9, 6))
    nx.draw(tree, pos=pos, labels=labels, arrows=False, node_size=2500, node_color=colors)
    plt.title("Візуалізація бінарної купи (дерево)")
    plt.tight_layout()
    plt.show()


def _heap_violations_indices(heap: List[float], kind: str = 'min') -> set:
    """
    Повертає множину індексів вузлів, що ПОРУШУЮТЬ властивість купи.
    - Для мін-купи: heap[i] <= heap[child]
    - Для макс-купи: heap[i] >= heap[child]
    Позначаємо порушення на батьківських вузлах (де знайдено конфлікт).
    """
    bad = set()
    n = len(heap)
    for i in range(n):
        li, ri = 2*i + 1, 2*i + 2
        if li < n:
            if (kind == 'min' and heap[i] > heap[li]) or (kind == 'max' and heap[i] < heap[li]):
                bad.add(i)
        if ri < n:
            if (kind == 'min' and heap[i] > heap[ri]) or (kind == 'max' and heap[i] < heap[ri]):
                bad.add(i)
    return bad


def heap_array_to_tree(heap: List[float], kind: str = 'min', color_ok: str = 'skyblue', color_bad: str = 'salmon') -> Node:
    """
    Створює дерево з масиву `heap`. Додатково підсвічує вузли з порушенням властивості купи.
    Повертає корінь дерева (Node).
    """
    if not heap:
        raise ValueError("Порожній масив купи.")

    bad = _heap_violations_indices(heap, kind=kind)

    # Створюємо вузли. Якщо індекс у 'bad' — фарбуємо у color_bad.
    nodes: List[Node] = []
    for i, val in enumerate(heap):
        color = color_bad if i in bad else color_ok
        nodes.append(Node(val, color=color))

    # Зв'язуємо дітей за індексами
    n = len(nodes)
    for i in range(n):
        li, ri = 2*i + 1, 2*i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]

    return nodes[0]  # корінь


def visualize_heap(heap: List[float], kind: str = 'min') -> None:
    """
    Візуалізація купи: будуємо дерево з масиву і малюємо.
    kind: 'min' або 'max' — тип купи (для перевірки та підсвічування).
    """
    root = heap_array_to_tree(heap, kind=kind)
    draw_tree(root)


# ---- Демонстрація ----
if __name__ == "__main__":
    # Мін-купа (валідна)
    min_heap = [1, 3, 2, 7, 8, 4, 5, 9, 10]
    print("Приклад мін-купи:", min_heap)
    visualize_heap(min_heap, kind='min')

    # Масив, що не відповідає мін-купі (буде підсвічено порушення у батьків)
    not_heap = [7, 3, 2, 1, 8, 4, 5]
    print("Масив з порушеннями для мін-купи:", not_heap)
    visualize_heap(not_heap, kind='min')