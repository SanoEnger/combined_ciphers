"""Маршрутная транспозиция: заполнение спиралью от центра против часовой, чтение — различными методами."""

from __future__ import annotations

import math

PAD_CHAR = "Х"

def calculate_matrix_size(text_length: int) -> tuple[int, int]:
    """
    Вычисляет оптимальный размер матрицы m x n для заданной длины текста
    (m и n как можно ближе друг к другу, m * n >= text_length)
    """
    if text_length <= 0:
        return 1, 1
    sqrt_len = math.sqrt(text_length)
    m = math.ceil(sqrt_len)
    n = math.ceil(text_length / m)
    while m * n < text_length:
        if m <= n:
            m += 1
        else:
            n += 1
    return m, n

def get_spiral_indices(m: int, n: int) -> list[tuple[int, int]]:
    """
    Порядок ячеек (строка, столбец): от центра, против часовой стрелки.
    Для любых m×n каждая ячейка ровно один раз (как в задаче «спираль от стартовой клетки»).
    Направления по кругу: вверх → влево → вниз → вправо.
    """
    if m < 1 or n < 1:
        raise ValueError("Размеры матрицы должны быть не меньше 1×1")
    total = m * n
    row, col = m // 2, n // 2
    positions: list[tuple[int, int]] = [(row, col)]
    if total == 1:
        return positions
    directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    dir_index = 0
    step_len = 1
    while len(positions) < total:
        for _ in range(2):
            for _ in range(step_len):
                row += directions[dir_index][0]
                col += directions[dir_index][1]
                if 0 <= row < m and 0 <= col < n:
                    positions.append((row, col))
            dir_index = (dir_index + 1) % 4
        step_len += 1
    return positions[:total]

def _matrix_from_rows(data: str, m: int, n: int) -> list[list[str]]:
    matrix: list[list[str]] = []
    k = 0
    for i in range(m):
        row: list[str] = []
        for j in range(n):
            row.append(data[k])
            k += 1
        matrix.append(row)
    return matrix

def _read_row_major(matrix: list[list[str]], m: int, n: int) -> str:
    """Построчно слева направо, сверху вниз"""
    return "".join(matrix[i][j] for i in range(m) for j in range(n))

def _read_snake_left_right(matrix: list[list[str]], m: int, n: int) -> str:
    """Змейкой: четные строки →, нечетные ←"""
    result = []
    for i in range(m):
        if i % 2 == 0:
            for j in range(n):
                result.append(matrix[i][j])
        else:
            for j in range(n-1, -1, -1):
                result.append(matrix[i][j])
    return "".join(result)

def _read_snake_right_left(matrix: list[list[str]], m: int, n: int) -> str:
    """Змейкой: четные строки ←, нечетные →"""
    result = []
    for i in range(m):
        if i % 2 == 0:
            for j in range(n-1, -1, -1):
                result.append(matrix[i][j])
        else:
            for j in range(n):
                result.append(matrix[i][j])
    return "".join(result)

def _read_snake_top_down(matrix: list[list[str]], m: int, n: int) -> str:
    """Змейкой по столбцам: четные столбцы ↓, нечетные ↑"""
    result = []
    for j in range(n):
        if j % 2 == 0:
            for i in range(m):
                result.append(matrix[i][j])
        else:
            for i in range(m-1, -1, -1):
                result.append(matrix[i][j])
    return "".join(result)

def _read_snake_bottom_up(matrix: list[list[str]], m: int, n: int) -> str:
    """Змейкой по столбцам снизу вверх"""
    result = []
    for j in range(n-1, -1, -1):
        if (n-1 - j) % 2 == 0:
            for i in range(m):
                result.append(matrix[i][j])
        else:
            for i in range(m-1, -1, -1):
                result.append(matrix[i][j])
    return "".join(result)

def _read_by_method(matrix: list[list[str]], m: int, n: int, method: str = "row") -> str:
    """Чтение матрицы выбранным методом"""
    methods = {
        "row": _read_row_major,
        "snake_left_right": _read_snake_left_right,
        "snake_right_left": _read_snake_right_left,
        "snake_top_down": _read_snake_top_down,
        "snake_bottom_up": _read_snake_bottom_up,
    }
    read_func = methods.get(method, _read_row_major)
    return read_func(matrix, m, n)

def transposition_encrypt(
    text: str,
    m: int,
    n: int,
    *,
    pad_char: str = PAD_CHAR,
    read_method: str = "row",
) -> tuple[str, str, int]:
    """
    Заполняет матрицу m×n по спирали от центра, списывает выбранным методом.
    Возвращает (шифртекст, текст с дополнением, сколько символов добавлено).
    """
    if m * n < 1:
        raise ValueError("Размер матрицы слишком маленький")
    cells = m * n
    upper = text.upper()
    if len(upper) > cells:
        raise ValueError(
            f"Текст длиннее, чем ячеек матрицы ({len(upper)} > {m}×{n} = {cells})"
        )
    pad_count = cells - len(upper)
    padded = upper + pad_char * pad_count
    spiral = get_spiral_indices(m, n)
    matrix: list[list[str]] = [["" for _ in range(n)] for _ in range(m)]
    for idx, (r, c) in enumerate(spiral):
        matrix[r][c] = padded[idx]
    ciphertext = _read_by_method(matrix, m, n, read_method)
    return ciphertext, padded, pad_count

def transposition_decrypt(
    ciphertext: str,
    m: int,
    n: int,
    read_method: str = "row",
) -> str:
    """
    Обратная операция: ввод шифртекста в матрицу выбранным методом чтения, чтение по спирали.
    """
    cells = m * n
    if len(ciphertext) != cells:
        raise ValueError(
            f"Длина шифртекста должна быть {cells} (сейчас {len(ciphertext)})"
        )
    
    # Создаем пустую матрицу
    matrix = [["" for _ in range(n)] for _ in range(m)]
    
    # Заполняем матрицу в соответствии с методом чтения (обратная операция)
    index = 0
    if read_method == "row":
        for i in range(m):
            for j in range(n):
                matrix[i][j] = ciphertext[index]
                index += 1
    elif read_method == "snake_left_right":
        for i in range(m):
            if i % 2 == 0:
                for j in range(n):
                    matrix[i][j] = ciphertext[index]
                    index += 1
            else:
                for j in range(n-1, -1, -1):
                    matrix[i][j] = ciphertext[index]
                    index += 1
    elif read_method == "snake_right_left":
        for i in range(m):
            if i % 2 == 0:
                for j in range(n-1, -1, -1):
                    matrix[i][j] = ciphertext[index]
                    index += 1
            else:
                for j in range(n):
                    matrix[i][j] = ciphertext[index]
                    index += 1
    elif read_method == "snake_top_down":
        for j in range(n):
            if j % 2 == 0:
                for i in range(m):
                    matrix[i][j] = ciphertext[index]
                    index += 1
            else:
                for i in range(m-1, -1, -1):
                    matrix[i][j] = ciphertext[index]
                    index += 1
    elif read_method == "snake_bottom_up":
        for j in range(n-1, -1, -1):
            if (n-1 - j) % 2 == 0:
                for i in range(m):
                    matrix[i][j] = ciphertext[index]
                    index += 1
            else:
                for i in range(m-1, -1, -1):
                    matrix[i][j] = ciphertext[index]
                    index += 1
    else:
        # По умолчанию построчно
        for i in range(m):
            for j in range(n):
                matrix[i][j] = ciphertext[index]
                index += 1
    
    spiral = get_spiral_indices(m, n)
    return "".join(matrix[r][c] for r, c in spiral)