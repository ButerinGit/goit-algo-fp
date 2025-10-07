"""
Завдання 7. Метод Монте-Карло: ймовірності сум при киданні двох кубиків.

Функціонал:
- Імітація кидків двох чесних кубиків (N разів).
- Підрахунок частот сум (2..12) і обчислення емпіричних ймовірностей.
- Порівняння з аналітичними ймовірностями, вивід таблиці різниць.
- Побудова стовпчикової діаграми емпіричних ймовірностей (збереження у PNG).

Запуск (приклади):
    python monte_carlo_dice.py --trials 200000 --seed 42 --save-plot probs.png

Параметри:
    --trials    кількість кидків (int, >= 1), за замовч. 100000
    --seed      (необов'язково) фіксація генератора випадкових чисел
    --save-plot шлях до файлу зображення PNG (необов'язково)
"""
import argparse
import random
from collections import Counter, OrderedDict

import matplotlib.pyplot as plt


def analytic_probs():
    """Аналітичні ймовірності сум (2..12) для двох чесних d6."""
    counts = {2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:5, 9:4, 10:3, 11:2, 12:1}
    total = 36
    return OrderedDict((s, c/total) for s, c in counts.items())


def simulate(trials: int, seed: int | None = None):
    """Імітувати кидання двох кубиків `trials` разів. Повертає OrderedDict сум→частота."""
    if seed is not None:
        random.seed(seed)
    ctr = Counter()
    for _ in range(trials):
        s = random.randint(1, 6) + random.randint(1, 6)
        ctr[s] += 1
    # Гарантуємо наявність усіх сум 2..12
    out = OrderedDict((s, ctr.get(s, 0)) for s in range(2, 13))
    return out


def main():
    parser = argparse.ArgumentParser(description="Метод Монте-Карло для двох кубиків")
    parser.add_argument("--trials", type=int, default=100000, help="Кількість кидків (за замовч. 100000)")
    parser.add_argument("--seed", type=int, default=None, help="Фіксований seed для відтворюваності")
    parser.add_argument("--save-plot", type=str, default=None, help="Файл для збереження графіка (PNG)")
    args = parser.parse_args()

    if args.trials < 1:
        raise ValueError("Кількість кидків має бути >= 1")

    theo = analytic_probs()
    freq = simulate(args.trials, seed=args.seed)
    emp = OrderedDict((s, freq[s] / args.trials) for s in freq.keys())

    # Вивід таблиці порівняння
    print("Сума | Емпірична ймовірність | Аналітична | Абс. похибка")
    print("-----+------------------------+------------+-------------")
    abs_errs = []
    for s in emp.keys():
        e = emp[s]
        t = theo[s]
        err = abs(e - t)
        abs_errs.append(err)
        print(f"{s:>4} | {e:>22.4%} | {t:>10.4%} | {err:>11.4%}")
    print("-" * 52)
    print(f"Середня абс. похибка: {sum(abs_errs)/len(abs_errs):.4%}")
    print(f"Макс.    абс. похибка: {max(abs_errs):.4%}")

    # Побудова графіка емпіричних ймовірностей
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(list(emp.keys()), list(emp.values()))
    ax.set_xlabel("Сума на двох кубиках")
    ax.set_ylabel("Ймовірність")
    ax.set_title(f"Емпіричні ймовірності (N={args.trials:,})")
    ax.set_xticks(list(emp.keys()))
    fig.tight_layout()
    if args.save_plot:
        fig.savefig(args.save_plot, dpi=160, bbox_inches="tight")
        print(f"Графік збережено до: {args.save_plot}")
    else:
        plt.show()


if __name__ == "__main__":
    main()