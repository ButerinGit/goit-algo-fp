"""
Візуалізація обходів бінарного дерева (DFS, BFS) БЕЗ рекурсії.
- Обходи виконуються за допомогою стеку (DFS) та черги (BFS).
- Кожен відвіданий вузол отримує унікальний колір у 16-ковому RGB (#RRGGBB),
  що змінюється від темного до світлого відтінку (одного тону).
- Кроки візуалізації показуються поступово (із паузою), можливе збереження кадрів.

Використано базові ідеї з завдання 4: структура Node, побудова графа та позицій для відображення.

Залежності:
    pip install networkx matplotlib

Приклади запуску:
    python tree_traversal_viz.py --mode dfs --pause 0.6
    python tree_traversal_viz.py --mode bfs --pause 0.4
    python tree_traversal_viz.py --mode bfs --values 0,4,1,5,10,3
    python tree_traversal_viz.py --mode dfs --save-frames frames_dfs

Параметри:
    --mode        dfs | bfs                (тип обходу)
    --pause       секунди між кроками      (float, за замовч. 0.5)
    --values      рівень-ордер список вузлів (через кому), напр.: 0,4,1,5,10,3
                  (None означає відсутність вузла)
    --save-frames папка для збереження PNG кадрів
"""

import uuid
from collections import deque
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import colorsys

import networkx as nx
import matplotlib.pyplot as plt


# ---------- Структура вузла ----------
class Node:
    def __init__(self, key, color: str = "#A0A0A0"):
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
        self.val = key
        self.color = color   # Початковий (нейтральний) колір
        self.id = str(uuid.uuid4())  # Унікальний ідентифікатор вузла


# ---------- Побудова графа і позицій (на основі завдання 4) ----------
def add_edges(graph: nx.DiGraph, node: Optional[Node], pos: Dict[str, Tuple[float, float]],
              x: float = 0, y: float = 0, layer: int = 1) -> nx.DiGraph:
    """
    Рекурсивно додає вершини/ребра у граф для відображення дерева.
    Примітка: тут допускаємо рекурсію лише для побудови зображення (НЕ для обходів).
    """
    if node is not None:
        graph.add_node(node.id, label=node.val)  # колір подамо окремо при малюванні
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


def build_graph_and_pos(root: Node) -> Tuple[nx.DiGraph, Dict[str, Tuple[float, float]], Dict[str, str]]:
    """Створити граф, позиції та мітки вузлів (id->label)."""
    tree = nx.DiGraph()
    pos = {root.id: (0, 0)}
    add_edges(tree, root, pos)
    labels = {node_id: data.get("label", "") for node_id, data in tree.nodes(data=True)}
    return tree, pos, labels


# ---------- Генерація відтінків HEX (темний -> світлий) ----------
def hls_to_hex(h: float, l: float, s: float) -> str:
    """Перетворення HLS (0..1) у HEX #RRGGBB."""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"


def generate_shades(n: int, hue_deg: float = 210.0, sat: float = 0.60,
                    light_start: float = 0.25, light_end: float = 0.85) -> List[str]:
    """
    Створити n відтінків одного тону (за замовч. синій, ~210°), від темного до світлого.
    Повертає список HEX-рядків.
    """
    if n <= 0:
        return []
    h = (hue_deg % 360.0) / 360.0
    if n == 1:
        return [hls_to_hex(h, (light_start + light_end) / 2.0, sat)]
    shades = []
    for i in range(n):
        l = light_start + (light_end - light_start) * (i / (n - 1))
        shades.append(hls_to_hex(h, l, sat))
    return shades


# ---------- Допоміжні функції ----------
def count_nodes(root: Optional[Node]) -> int:
    if not root:
        return 0
    q = deque([root])
    c = 0
    while q:
        n = q.popleft()
        if n is None:
            continue
        c += 1
        if n.left:
            q.append(n.left)
        if n.right:
            q.append(n.right)
    return c


def build_tree_from_level_list(values: List[Optional[str]]) -> Optional[Node]:
    """
    Побудова дерева з рівень-ордер представлення (масив), де None = відсутній вузол.
    Індекси: i -> left=2*i+1, right=2*i+2.
    """
    if not values:
        return None
    nodes = [Node(v) if v is not None else None for v in values]
    n = len(nodes)
    for i, node in enumerate(nodes):
        if node is None:
            continue
        li, ri = 2*i + 1, 2*i + 2
        if li < n:
            node.left = nodes[li]
        if ri < n:
            node.right = nodes[ri]
    return nodes[0]


# ---------- Ітеративні обходи (БЕЗ рекурсії) ----------
def dfs_iter(root: Optional[Node]):
    """Ітеративний DFS (preorder): стек. Лівий перед правим (push правого першим)."""
    if root is None:
        return
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        yield node
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)


def bfs_iter(root: Optional[Node]):
    """Ітеративний BFS: черга зліва направо."""
    if root is None:
        return
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            continue
        yield node
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)


# ---------- Візуалізація кроків ----------
def draw_step(ax, tree: nx.DiGraph, pos: Dict[str, Tuple[float, float]], labels: Dict[str, str],
              color_map: Dict[str, str], neutral_color: str = "#A0A0A0",
              title: str = ""):
    ax.clear()
    # Масив кольорів у порядку node-list графа
    colors = [color_map.get(n_id, neutral_color) for n_id in tree.nodes()]
    nx.draw(tree, pos=pos, labels=labels, arrows=False, node_size=2500, node_color=colors, ax=ax)
    ax.set_title(title)
    ax.set_axis_off()


def visualize_traversal(root: Node, mode: str = "dfs", pause: float = 0.5,
                        save_frames: Optional[str] = None, hue_deg: float = 210.0):
    """
    Поступова візуалізація обходу дерева (dfs/bfs), фарбуючи відвідані вузли
    у відтінки від темного до світлого.
    """
    tree, pos, labels = build_graph_and_pos(root)

    n = count_nodes(root)
    shades = generate_shades(n, hue_deg=hue_deg)
    color_map: Dict[str, str] = {}

    it = dfs_iter(root) if mode.lower() == "dfs" else bfs_iter(root)

    # Підготовка фігури
    fig, ax = plt.subplots(figsize=(9, 6))

    # Початковий стан
    draw_step(ax, tree, pos, labels, color_map, title=f"{mode.upper()} — крок 0/{n}")
    plt.pause(pause)

    # Поступове фарбування
    step = 0
    frames_dir = None
    if save_frames:
        frames_dir = Path(save_frames)
        frames_dir.mkdir(parents=True, exist_ok=True)

    for node in it:
        color_map[node.id] = shades[step]
        step += 1
        draw_step(ax, tree, pos, labels, color_map, title=f"{mode.upper()} — крок {step}/{n}")
        if frames_dir is not None:
            fig.savefig(frames_dir / f"step_{step:03d}.png", dpi=160, bbox_inches="tight")
        plt.pause(pause)

    # Завершальний кадр
    if frames_dir is not None:
        fig.savefig(frames_dir / f"final_{mode}.png", dpi=160, bbox_inches="tight")
    plt.show()


# ---------- Демонстрація ----------
def demo_root() -> Node:
    """Приклад дерева з умови (можна змінювати)."""
    root = Node(0)
    root.left = Node(4)
    root.left.left = Node(5)
    root.left.right = Node(10)
    root.right = Node(1)
    root.right.left = Node(3)
    return root


def parse_values_arg(values_arg: Optional[str]) -> Optional[Node]:
    """Парсинг --values у дерево. Формат: 0,4,1,5,10,3 або з None: 1,2,3,None,5."""
    if not values_arg:
        return None
    raw = [s.strip() for s in values_arg.split(",")]
    vals: List[Optional[str]] = []
    for x in raw:
        if x.lower() == "none":
            vals.append(None)
        else:
            # Спробуємо конвертувати у int, якщо можливо; інакше лишаємо рядок
            try:
                vals.append(int(x))
            except ValueError:
                vals.append(x)
    return build_tree_from_level_list(vals)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Візуалізація обходів бінарного дерева без рекурсії (DFS/BFS)." )
    parser.add_argument("--mode", choices=["dfs", "bfs"], default="dfs", help="Тип обходу." )
    parser.add_argument("--pause", type=float, default=0.5, help="Пауза між кроками (секунди)." )
    parser.add_argument("--values", type=str, default=None, help="Рівень-ордер список вузлів (через кому)." )
    parser.add_argument("--save-frames", type=str, default=None, help="Папка для збереження PNG кадрів." )
    parser.add_argument("--hue", type=float, default=210.0, help="Відтінок (градуси H, 0..360) — за замовч. синій." )
    args = parser.parse_args()

    root = parse_values_arg(args.values) or demo_root()
    visualize_traversal(root, mode=args.mode, pause=args.pause, save_frames=args.save_frames, hue_deg=args.hue)


if __name__ == "__main__":
    main()