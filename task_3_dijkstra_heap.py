"""
Алгоритм Дейкстри з використанням бінарної купи (heapq) для пошуку найкоротших шляхів
у зваженому орієнтованому або неорієнтованому графі з невід'ємними вагами ребер.

Можливості:
- Створення графа на основі списку ребер (u, v, w).
- Додавання ребер до графа через метод add_edge.
- Запуск алгоритму Дейкстри з вибраної стартової вершини (повертає відстані та попередники).
- Відновлення (реконструкція) конкретного шляху до цільової вершини.
- Демонстраційний приклад у блоці __main__.
- (Необов'язково) Читання ребер із CSV/TSV-файлу за ключем --edges.

Приклади запуску:
    python dijkstra_heap.py --source A
    python dijkstra_heap.py --source A --undirected
    python dijkstra_heap.py --source 0 --edges edges.csv --delimiter , --undirected
"""

from __future__ import annotations

import argparse
import csv
import heapq
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional


class Graph:
    """
    Граф на основі списків суміжності.
    Вузли можуть бути будь-якими хешовними об'єктами (рядки, числа тощо).
    """
    def __init__(self) -> None:
        # adj[u] = список пар (v, w), де w >= 0 — вага ребра u->v
        self.adj: Dict[Any, List[Tuple[Any, float]]] = defaultdict(list)

    def add_edge(self, u: Any, v: Any, w: float, undirected: bool = False) -> None:
        """
        Додати ребро u->v з вагою w. Якщо undirected=True, додається також v->u.
        Перевірка на невід'ємність ваги (вимога алгоритму Дейкстри).
        """
        if w < 0:
            raise ValueError("Алгоритм Дейкстри не підтримує від'ємні ваги ребер.")
        self.adj[u].append((v, float(w)))
        # Гарантуємо наявність вершини v у словнику навіть без вихідних ребер
        if v not in self.adj:
            self.adj[v] = []
        if undirected:
            self.adj[v].append((u, float(w)))

    def dijkstra(self, source: Any) -> Tuple[Dict[Any, float], Dict[Any, Optional[Any]]]:
        """
        Алгоритм Дейкстри з використанням бінарної купи (heapq).
        Повертає:
          - dist: найкоротші відстані від source до всіх вершин
          - prev: попередник для кожної вершини у найкоротшому шляху (для реконструкції маршруту)
        """
        # Ініціалізація відстаней нескінченністю
        dist: Dict[Any, float] = {u: float('inf') for u in self.adj}
        prev: Dict[Any, Optional[Any]] = {u: None for u in self.adj}
        if source not in self.adj:
            raise KeyError(f"Стартова вершина {source!r} відсутня у графі.")

        dist[source] = 0.0
        # Бінарна купа з кортежами (поточна_відстань, вершина)
        heap: List[Tuple[float, Any]] = [(0.0, source)]

        while heap:
            d_u, u = heapq.heappop(heap)
            # Якщо знайшли у купі застарілий запис — пропускаємо
            if d_u != dist[u]:
                continue

            # Релаксація ребер з u
            for v, w in self.adj[u]:
                alt = d_u + w
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    # Додаємо у купу нову кращу оцінку для v
                    heapq.heappush(heap, (alt, v))

        return dist, prev

    @staticmethod
    def reconstruct_path(prev: Dict[Any, Optional[Any]], target: Any) -> List[Any]:
        """
        Відновити шлях до вершини target, використовуючи словник попередників prev.
        Якщо шляху не існує — повертає порожній список.
        """
        if target not in prev:
            return []
        path: List[Any] = []
        cur: Optional[Any] = target
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path


def read_edges_from_file(path: str, delimiter: str = ",", undirected: bool = False) -> Graph:
    """
    Зчитати ребра з CSV/TSV файлу.
    Очікується щонайменше 3 колонки: u, v, w (вага). Інші колонки ігноруються.
    """
    g = Graph()
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if len(row) < 3:
                continue
            u, v, w = row[0], row[1], float(row[2])
            g.add_edge(u, v, w, undirected=undirected)
    return g


def demo_graph(undirected: bool = False) -> Graph:
    """
    Демонстраційний граф (невеликий приклад).
    Вузли: A, B, C, D, E.
    """
    edges = [
        ("A", "B", 4),
        ("A", "C", 2),
        ("B", "C", 1),
        ("B", "D", 5),
        ("C", "D", 8),
        ("C", "E", 10),
        ("D", "E", 2),
        ("B", "E", 6),
    ]
    g = Graph()
    for u, v, w in edges:
        g.add_edge(u, v, w, undirected=undirected)
    return g


def main() -> None:
    parser = argparse.ArgumentParser(description="Алгоритм Дейкстри з бінарною купою (heapq)." )
    parser.add_argument("--source", required=True, help="Стартова вершина (ідентифікатор вузла)." )
    parser.add_argument("--edges", type=str, default=None, help="Шлях до CSV/TSV файлу з ребрами (u,v,w)." )
    parser.add_argument("--delimiter", type=str, default=",", help="Роздільник у файлі ребер (за замовч. кома)." )
    parser.add_argument("--undirected", action="store_true", help="Розглядати граф як неорієнтований." )
    args = parser.parse_args()

    # 1) Створюємо граф: або читаємо з файлу, або беремо демонстраційний
    if args.edges:
        g = read_edges_from_file(args.edges, delimiter=args.delimiter, undirected=args.undirected)
    else:
        g = demo_graph(undirected=args.undirected)

    # 2) Запускаємо Дейкстру
    dist, prev = g.dijkstra(args.source)

    # 3) Виводимо результати
    print("Найкоротші відстані від вершини", args.source)
    for node in sorted(g.adj.keys(), key=lambda x: str(x)):
        d = dist[node]
        if d == float('inf'):
            print(f"  {node}: немає шляху")
        else:
            print(f"  {node}: {d}")

    # 4) Приклад відновлення шляху до кожної вершини
    print("\nВідновлені шляхи:")
    for node in sorted(g.adj.keys(), key=lambda x: str(x)):
        path = Graph.reconstruct_path(prev, node)
        if path and path[0] == args.source:
            print(f"  {args.source} -> {node}: {' -> '.join(map(str, path))}")
        else:
            print(f"  {args.source} -> {node}: шляху немає")


if __name__ == "__main__":
    main()