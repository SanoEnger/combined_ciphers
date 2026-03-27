"""Маршрутная транспозиция: заполнение спиралью от центра против часовой, чтение — построчно слева направо."""

from __future__ import annotations

PAD_CHAR = "Х"


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


def _read_rows_left_right(matrix: list[list[str]], m: int, n: int) -> str:
    return "".join(matrix[i][j] for i in range(m) for j in range(n))


def transposition_encrypt(
    text: str,
    m: int,
    n: int,
    *,
    pad_char: str = PAD_CHAR,
) -> tuple[str, str, int]:
    """
    Заполняет матрицу m×n по спирали от центра, списывает построчно (слева направо, сверху вниз).
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
    ciphertext = _read_rows_left_right(matrix, m, n)
    return ciphertext, padded, pad_count


def transposition_decrypt(
    ciphertext: str,
    m: int,
    n: int,
) -> str:
    """Обратная операция: ввод шифртекста в матрицу по строкам, чтение по спирали."""
    cells = m * n
    if len(ciphertext) != cells:
        raise ValueError(
            f"Длина шифртекста должна быть {cells} (сейчас {len(ciphertext)})"
        )
    matrix = _matrix_from_rows(ciphertext, m, n)
    spiral = get_spiral_indices(m, n)
    return "".join(matrix[r][c] for r, c in spiral)
