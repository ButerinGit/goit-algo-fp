"""
Фрактал "Дерево Піфагора" з використанням рекурсії.
- Візуалізація класичного дерева Піфагора, яке складається з квадратів.
- Користувач може задати рівень рекурсії, кут відгалуження та розмір базового квадрата.
- Можливість збереження зображення у файл.

Приклади запуску:
    python pythagoras_tree.py --level 10
    python pythagoras_tree.py --level 12 --angle 45 --size 1.0 --save tree.png
    python pythagoras_tree.py --level 9 --angle 35 --no-show
"""
import argparse
import math
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def square_corners(x, y, s, a_rad):
    """
    Обчислення координат кутів квадрата.

    Аргументи:
      - (x, y): координати нижнього лівого кута квадрата
      - s: довжина сторони квадрата
      - a_rad: кут повороту у радіанах (0 означає вздовж осі +x)

    Повертає список з 4 кутів (p0 - лівий нижній, p1 - правий нижній, p2 - правий верхній, p3 - лівий верхній).
    """
    ca, sa = math.cos(a_rad), math.sin(a_rad)
    dx, dy = s * ca, s * sa
    nx, ny = -s * sa, s * ca

    p0 = (x, y)
    p1 = (x + dx, y + dy)
    p2 = (x + dx + nx, y + dy + ny)
    p3 = (x + nx, y + ny)
    return [p0, p1, p2, p3]


def draw_square(ax, corners):
    """Намалювати квадрат за заданими кутами."""
    poly = Polygon(corners, closed=True, fill=True, edgecolor="black", linewidth=0.5)
    ax.add_patch(poly)


def recurse_tree(ax, x, y, s, a_rad, level, theta_rad):
    """
    Рекурсивне малювання дерева Піфагора.

    Аргументи:
      - ax: вісі matplotlib
      - (x, y): нижній лівий кут поточного квадрата
      - s: довжина сторони квадрата
      - a_rad: орієнтація квадрата (у радіанах)
      - level: глибина рекурсії (ціле число >=0)
      - theta_rad: кут відгалуження у радіанах (0 < theta < 90 градусів)
    """
    if level < 0 or s <= 0:
        return

    # Малюємо поточний квадрат
    corners = square_corners(x, y, s, a_rad)
    draw_square(ax, corners)

    if level == 0:
        return

    # Розкладаємо кути
    p0, p1, p2, p3 = corners

    # Вектор верхнього ребра (p3->p2)
    ux = p2[0] - p3[0]
    uy = p2[1] - p3[1]
    ulen = math.hypot(ux, uy)
    ux /= ulen
    uy /= ulen
    # Перпендикулярний вектор
    vx = -uy
    vy = ux

    # Обчислення довжин сторін дочірніх квадратів
    s_left = s * math.cos(theta_rad)
    s_right = s * math.sin(theta_rad)

    # Точка вершини прямокутного трикутника
    apex_x = p3[0] + ux * s_left + vx * s_right
    apex_y = p3[1] + uy * s_left + vy * s_right

    # Ліва гілка
    recurse_tree(ax, p3[0], p3[1], s_left, a_rad + theta_rad, level - 1, theta_rad)

    # Права гілка
    recurse_tree(ax, apex_x, apex_y, s_right, a_rad + theta_rad - math.pi / 2, level - 1, theta_rad)


def compute_extent(level, size, angle_deg):
    """Оцінка меж графіка для відображення всього дерева."""
    a = math.radians(angle_deg)
    growth = (math.cos(a) + math.sin(a)) ** level
    margin = size * (0.2 + 0.15 * level)
    width = size * (1 + growth)
    xmin = -margin
    xmax = width + margin
    ymin = -margin * 0.3
    ymax = size * (1 + 0.8 * growth) + margin
    return xmin, xmax, ymin, ymax


def main():
    parser = argparse.ArgumentParser(description="Фрактал 'Дерево Піфагора' (рекурсивно)." )
    parser.add_argument("--level", type=int, default=10, help="Рівень рекурсії (наприклад, 8..13)." )
    parser.add_argument("--angle", type=float, default=45.0, help="Кут відгалуження у градусах (0<кут<90)." )
    parser.add_argument("--size", type=float, default=1.0, help="Довжина сторони базового квадрата." )
    parser.add_argument("--save", type=str, default=None, help="Шлях для збереження зображення (наприклад, output.png)." )
    parser.add_argument("--no-show", action="store_true", help="Не відкривати вікно (корисно на сервері)." )
    args = parser.parse_args()

    if not (0.0 < args.angle < 90.0):
        print("Кут має бути між 0 та 90 градусами.", file=sys.stderr)
        sys.exit(1)
    if args.level < 0:
        print("Рівень рекурсії має бути невід'ємним.", file=sys.stderr)
        sys.exit(1)

    theta_rad = math.radians(args.angle)

    fig, ax = plt.subplots(figsize=(8, 8))
    # Малюємо базовий квадрат (нижній лівий кут в (0,0))
    recurse_tree(ax, x=0.0, y=0.0, s=args.size, a_rad=0.0, level=args.level, theta_rad=theta_rad)

    # Встановлюємо межі графіка
    xmin, xmax, ymin, ymax = compute_extent(args.level, args.size, args.angle)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout(pad=0.1)

    if args.save:
        fig.savefig(args.save, dpi=200, bbox_inches="tight")
        print(f"Зображення збережено у файл: {args.save}")

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()