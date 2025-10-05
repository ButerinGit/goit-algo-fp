"""
Завдання 6. Жадібні алгоритми та динамічне програмування
--------------------------------------------------------
Проблема: обрати набір страв з максимальною сумарною калорійністю, не перевищивши бюджет.
Представлення: словник items: {name: {"cost": int, "calories": int}, ...}

Реалізовано два підходи:
1) greedy_algorithm(items, budget): жадібний вибір за найбільшим співвідношенням калорій/вартість.
   (Жадібний підхід НЕ гарантує оптимальності для задачі 0/1-рюкзака, але швидкий і простий.)
2) dynamic_programming(items, budget): класичний 0/1-рюкзак (DP) — гарантує оптимальний результат.

Запуск з CLI (приклади):
    python meal_selection.py --budget 100                  # показати обидва підходи
    python meal_selection.py --budget 75 --strategy greedy # лише жадібний
    python meal_selection.py --budget 75 --strategy dp     # лише ДП

Авторський набір із умови (можна змінювати):
    items = {
      "pizza": {"cost": 50, "calories": 300},
      "hamburger": {"cost": 40, "calories": 250},
      "hot-dog": {"cost": 30, "calories": 200},
      "pepsi": {"cost": 10, "calories": 100},
      "cola": {"cost": 15, "calories": 220},
      "potato": {"cost": 25, "calories": 350}
    }
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Tuple


# ---------- Дані з умови ----------
DEFAULT_ITEMS: Dict[str, Dict[str, int]] = {
    "pizza": {"cost": 50, "calories": 300},
    "hamburger": {"cost": 40, "calories": 250},
    "hot-dog": {"cost": 30, "calories": 200},
    "pepsi": {"cost": 10, "calories": 100},
    "cola": {"cost": 15, "calories": 220},
    "potato": {"cost": 25, "calories": 350},
}


# ---------- Жадібний алгоритм ----------
def greedy_algorithm(items: Dict[str, Dict[str, int]], budget: int) -> Tuple[List[str], int, int]:
    """
    Жадібно відбирає страви за спаданням співвідношення (calories / cost),
    не перевищуючи бюджет.

    Повертає кортеж: (список_страв, загальна_вартість, загальні_калорії).
    """
    # Формуємо список з полями та коефіцієнтом «калорії/вартість»
    goods = []
    for name, info in items.items():
        cost = int(info["cost"])
        calories = int(info["calories"])
        ratio = calories / cost if cost > 0 else 0
        goods.append((name, cost, calories, ratio))

    # Сортуємо: найбільший ratio -> першим; при однаковому ratio — дешевші раніше
    goods.sort(key=lambda x: (-x[3], x[1], -x[2]))

    selected: List[str] = []
    total_cost = 0
    total_cal = 0
    remaining = budget

    for name, cost, calories, ratio in goods:
        if cost <= remaining:
            selected.append(name)
            total_cost += cost
            total_cal += calories
            remaining -= cost

    return selected, total_cost, total_cal


# ---------- Динамічне програмування (0/1-рюкзак) ----------
def dynamic_programming(items: Dict[str, Dict[str, int]], budget: int) -> Tuple[List[str], int, int]:
    """
    Оптимальний відбір страв методом ДП (0/1-knapsack).
    Вартість — «вага», калорії — «користь». Кожну страву можна взяти НЕ більше одного разу.

    Повертає кортеж: (список_страв, загальна_вартість, загальні_калорії).
    """
    names = list(items.keys())
    costs = [int(items[n]["cost"]) for n in names]
    calories = [int(items[n]["calories"]) for n in names]
    n = len(names)
    W = int(budget)

    # dp[i][w] — макс. калорії, використовуючи перші i предметів та бюджет w
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        c = costs[i - 1]
        cal = calories[i - 1]
        for w in range(W + 1):
            dp[i][w] = dp[i - 1][w]  # не беремо i-й
            if c <= w:
                cand = dp[i - 1][w - c] + cal  # беремо i-й
                if cand > dp[i][w]:
                    dp[i][w] = cand

    # Реконструкція набору
    w = W
    selected_idx: List[int] = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:  # i-й предмет було взято
            selected_idx.append(i - 1)
            w -= costs[i - 1]

    selected_idx.reverse()
    selected = [names[i] for i in selected_idx]
    total_cost = sum(costs[i] for i in selected_idx)
    total_cal = dp[n][W]
    return selected, total_cost, total_cal


# ---------- Допоміжний вивід ----------
def print_solution(title: str, selected: List[str], total_cost: int, total_cal: int) -> None:
    print(f"\n{title}:" )
    if not selected:
        print("  Нічого не вибрано.")
        print(f"  Сумарна вартість: 0 | Сумарні калорії: 0" )
        return
    print("  Набір страв:", ", ".join(selected))
    print(f"  Сумарна вартість: {total_cost}")
    print(f"  Сумарні калорії: {total_cal}")


def main():
    parser = argparse.ArgumentParser(description="Вибір їжі за бюджетом: жадібний підхід та динамічне програмування." )
    parser.add_argument("--budget", type=int, required=True, help="Бюджет (ціле число)." )
    parser.add_argument("--strategy", choices=["greedy", "dp", "both"], default="both",
                        help="Яку стратегію виконати." )
    args = parser.parse_args()

    items = DEFAULT_ITEMS
    B = args.budget

    if args.strategy in ("greedy", "both"):
        g_sel, g_cost, g_cal = greedy_algorithm(items, B)
        print_solution("Жадібний алгоритм", g_sel, g_cost, g_cal)

    if args.strategy in ("dp", "both"):
        d_sel, d_cost, d_cal = dynamic_programming(items, B)
        print_solution("Динамічне програмування (оптимально)", d_sel, d_cost, d_cal)


if __name__ == "__main__":
    main()