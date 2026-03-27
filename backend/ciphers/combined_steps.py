"""Пошаговые сценарии шифрования и расшифрования для API обучения."""

from __future__ import annotations

from typing import Any

from .substitution import RUSSIAN_ALPHABET, create_substitution_alphabets, substitute_decrypt, substitute_encrypt
from .transposition import PAD_CHAR, get_spiral_indices, transposition_decrypt, transposition_encrypt


def _normalize_sub_text(text: str) -> str:
    return "".join(ch.upper() for ch in text if ch.upper() in RUSSIAN_ALPHABET)


def _normalize_trans_text(text: str) -> str:
    return "".join(ch.upper() for ch in text if ch.upper() in RUSSIAN_ALPHABET)


def _sub_visualization(key: str) -> dict[str, Any]:
    shifts = create_substitution_alphabets(key, RUSSIAN_ALPHABET)
    period = len(shifts)
    rows = []
    for i in range(period):
        rows.append(
            {
                "position_in_period": i + 1,
                "shifted_alphabet": shifts[i],
            }
        )
    return {
        "type": "substitution",
        "keyword": key.upper(),
        "period": period,
        "base_alphabet": RUSSIAN_ALPHABET,
        "rows": rows,
    }


def _trans_visualization(m: int, n: int, matrix: list[list[str]], spiral: list[tuple[int, int]]) -> dict[str, Any]:
    return {
        "type": "transposition",
        "m": m,
        "n": n,
        "matrix": matrix,
        "spiral_order": [{"row": r, "col": c} for r, c in spiral],
        "read_order": "row_major",
        "read_description": "Построчно слева направо, сверху вниз",
    }


def get_encryption_steps(
    text: str,
    mode: str,
    sub_key: str | None = None,
    m: int | None = None,
    n: int | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """
    Возвращает (список шагов, финальный текст).
    Каждый шаг: step, title, description, text, visualization.
    """
    steps: list[dict[str, Any]] = []
    sub_key = (sub_key or "").strip()

    if mode == "substitution":
        if not sub_key:
            raise ValueError("Ключ не может быть пустым")
        plain = _normalize_sub_text(text)
        if not plain:
            raise ValueError("В тексте нет букв русского алфавита")
        steps.append(
            {
                "step": 1,
                "title": "Исходный текст",
                "description": "То, что нужно зашифровать. Лишние символы не используются.",
                "text": plain,
                "visualization": {"type": "plain", "alphabet_note": "Используется алфавит из 33 букв (есть буква Ё)."},
            }
        )
        out = substitute_encrypt(plain, sub_key, RUSSIAN_ALPHABET)
        steps.append(
            {
                "step": 2,
                "title": "После замены",
                "description": (
                    f"Мы по очереди брали буквы из {len(sub_key)} разных шифрующих алфавитов "
                    f'по ключу «{sub_key.upper()}». Каждая буква заменялась на букву с тем же номером '
                    "в своём алфавите."
                ),
                "text": out,
                "visualization": _sub_visualization(sub_key),
            }
        )
        return steps, out

    if mode == "transposition":
        if m is None or n is None:
            raise ValueError("Укажите размер матрицы: m и n")
        if m < 2 or n < 2:
            raise ValueError("Размер матрицы слишком маленький (нужно хотя бы 2×2)")
        plain = _normalize_trans_text(text)
        if not plain:
            raise ValueError("В тексте нет букв русского алфавита")
        spiral = get_spiral_indices(m, n)
        ct, padded, pad_count = transposition_encrypt(plain, m, n)
        matrix: list[list[str]] = [["" for _ in range(n)] for _ in range(m)]
        for idx, (r, c) in enumerate(spiral):
            matrix[r][c] = padded[idx]
        steps.append(
            {
                "step": 1,
                "title": "Исходный текст",
                "description": "Буквы приводятся к верхнему регистру; пробелы и знаки не входят в таблицу.",
                "text": plain,
                "visualization": {"type": "plain"},
            }
        )
        pad_note = (
            f"В конец добавлено символов «{PAD_CHAR}»: {pad_count}, чтобы длина стала {m}×{n} = {m * n}."
            if pad_count
            else "Дополнение не понадобилось — букв ровно столько, сколько ячеек."
        )
        steps.append(
            {
                "step": 2,
                "title": "После перестановки",
                "description": (
                    "Сначала буквы по очереди кладутся в таблицу по спирали от центра против часовой стрелки. "
                    "Потом зашифрованный текст читают обычно: с первой строки слева направо, потом вторая строка, "
                    "и так далее. " + pad_note
                ),
                "text": ct,
                "visualization": {
                    **_trans_visualization(m, n, matrix, spiral),
                    "padded_block": padded,
                    "padding_added": pad_count,
                    "pad_char": PAD_CHAR,
                },
            }
        )
        return steps, ct

    if mode == "sub_then_trans":
        if not sub_key:
            raise ValueError("Ключ не может быть пустым")
        if m is None or n is None:
            raise ValueError("Укажите размер матрицы: m и n")
        if m < 2 or n < 2:
            raise ValueError("Размер матрицы слишком маленький (нужно хотя бы 2×2)")
        plain = _normalize_sub_text(text)
        if not plain:
            raise ValueError("В тексте нет букв русского алфавита")
        steps.append(
            {
                "step": 1,
                "title": "Исходный текст",
                "description": "Сначала будет шифр замены, затем — перестановка в таблице.",
                "text": plain,
                "visualization": {"type": "plain"},
            }
        )
        mid = substitute_encrypt(plain, sub_key, RUSSIAN_ALPHABET)
        steps.append(
            {
                "step": 2,
                "title": "После замены",
                "description": (
                    f"Промежуточный текст получен лозунговой заменой по ключу «{sub_key.upper()}». "
                    f"Используется {len(sub_key)} разных алфавитов по очереди."
                ),
                "text": mid,
                "visualization": _sub_visualization(sub_key),
            }
        )
        spiral = get_spiral_indices(m, n)
        ct, padded, pad_count = transposition_encrypt(mid, m, n)
        matrix = [["" for _ in range(n)] for _ in range(m)]
        for idx, (r, c) in enumerate(spiral):
            matrix[r][c] = padded[idx]
        pad_note = (
            f"Добавлено символов «{PAD_CHAR}»: {pad_count}."
            if pad_count
            else "Дополнение не нужно."
        )
        steps.append(
            {
                "step": 3,
                "title": "После перестановки",
                "description": (
                    "К промежуточному тексту применяется перестановка: спираль от центра, "
                    "чтение построчно. " + pad_note
                ),
                "text": ct,
                "visualization": {
                    **_trans_visualization(m, n, matrix, spiral),
                    "padded_block": padded,
                    "padding_added": pad_count,
                    "pad_char": PAD_CHAR,
                },
            }
        )
        return steps, ct

    if mode == "trans_then_sub":
        if not sub_key:
            raise ValueError("Ключ не может быть пустым")
        if m is None or n is None:
            raise ValueError("Укажите размер матрицы: m и n")
        if m < 2 or n < 2:
            raise ValueError("Размер матрицы слишком маленький (нужно хотя бы 2×2)")
        plain = _normalize_trans_text(text)
        if not plain:
            raise ValueError("В тексте нет букв русского алфавита")
        steps.append(
            {
                "step": 1,
                "title": "Исходный текст",
                "description": "Сначала перестановка в таблице, потом шифр замены.",
                "text": plain,
                "visualization": {"type": "plain"},
            }
        )
        spiral = get_spiral_indices(m, n)
        mid, padded, pad_count = transposition_encrypt(plain, m, n)
        matrix = [["" for _ in range(n)] for _ in range(m)]
        for idx, (r, c) in enumerate(spiral):
            matrix[r][c] = padded[idx]
        pad_note = (
            f"Добавлено «{PAD_CHAR}»: {pad_count}." if pad_count else "Без дополнения."
        )
        steps.append(
            {
                "step": 2,
                "title": "После перестановки",
                "description": "Промежуточный текст после заполнения спиралью и чтения по строкам. " + pad_note,
                "text": mid,
                "visualization": {
                    **_trans_visualization(m, n, matrix, spiral),
                    "padded_block": padded,
                    "padding_added": pad_count,
                    "pad_char": PAD_CHAR,
                },
            }
        )
        out = substitute_encrypt(mid, sub_key, RUSSIAN_ALPHABET)
        steps.append(
            {
                "step": 3,
                "title": "После замены",
                "description": f"К промежуточному тексту применена лозунговая замена по ключу «{sub_key.upper()}».",
                "text": out,
                "visualization": _sub_visualization(sub_key),
            }
        )
        return steps, out

    raise ValueError(f"Неизвестный режим: {mode}")


def get_decryption_steps(
    text: str,
    mode: str,
    sub_key: str | None = None,
    m: int | None = None,
    n: int | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Расшифрование — обратный порядок операций относительно шифрования."""
    steps: list[dict[str, Any]] = []
    sub_key = (sub_key or "").strip()

    if mode == "substitution":
        if not sub_key:
            raise ValueError("Ключ не может быть пустым")
        cipher = _normalize_sub_text(text)
        if not cipher:
            raise ValueError("В тексте нет букв русского алфавита")
        steps.append(
            {
                "step": 1,
                "title": "Введённый шифртекст",
                "description": "Символы вне алфавита отбрасываются.",
                "text": cipher,
                "visualization": {"type": "cipher_input"},
            }
        )
        out = substitute_decrypt(cipher, sub_key, RUSSIAN_ALPHABET)
        steps.append(
            {
                "step": 2,
                "title": "После расшифровки замены",
                "description": "Каждая буква возвращается с помощью обратных алфавитов по тому же ключу.",
                "text": out,
                "visualization": _sub_visualization(sub_key),
            }
        )
        return steps, out

    if mode == "transposition":
        if m is None or n is None:
            raise ValueError("Укажите размер матрицы: m и n")
        if m < 2 or n < 2:
            raise ValueError("Размер матрицы слишком маленький (нужно хотя бы 2×2)")
        cipher = _normalize_trans_text(text)
        if len(cipher) != m * n:
            raise ValueError(
                f"Длина шифртекста должна быть {m}×{n} = {m * n} (сейчас {len(cipher)} букв)"
            )
        spiral = get_spiral_indices(m, n)
        plain = transposition_decrypt(cipher, m, n)
        matrix: list[list[str]] = [["" for _ in range(n)] for _ in range(m)]
        k = 0
        for i in range(m):
            for j in range(n):
                matrix[i][j] = cipher[k]
                k += 1
        steps.append(
            {
                "step": 1,
                "title": "Введённый шифртекст",
                "description": "Буквы записываются в таблицу по строкам; потом читаются по спирали от центра.",
                "text": cipher,
                "visualization": {"type": "cipher_input"},
            }
        )
        steps.append(
            {
                "step": 2,
                "title": "После расшифровки перестановки",
                "description": "Получен текст до перестановки (в конце могут быть лишние «Х», если они были дополнением).",
                "text": plain,
                "visualization": {
                    **_trans_visualization(m, n, matrix, spiral),
                    "note": "Шифртекст заносился в таблицу построчно; чтение — по спирали, как при зашифровании в обратную сторону.",
                },
            }
        )
        return steps, plain

    if mode == "sub_then_trans":
        # Зашифрование было: замена → перестановка. Расшифрование: сначала перестановка, потом замена.
        if not sub_key:
            raise ValueError("Ключ не может быть пустым")
        if m is None or n is None:
            raise ValueError("Укажите размер матрицы: m и n")
        if m < 2 or n < 2:
            raise ValueError("Размер матрицы слишком маленький (нужно хотя бы 2×2)")
        cipher = _normalize_trans_text(text)
        if len(cipher) != m * n:
            raise ValueError(
                f"Длина шифртекста должна быть {m * n} (сейчас {len(cipher)})"
            )
        steps.append(
            {
                "step": 1,
                "title": "Введённый шифртекст",
                "description": "Сначала снимаем перестановку, потом — замену.",
                "text": cipher,
                "visualization": {"type": "cipher_input"},
            }
        )
        spiral = get_spiral_indices(m, n)
        mid = transposition_decrypt(cipher, m, n)
        matrix = [["" for _ in range(n)] for _ in range(m)]
        k = 0
        for i in range(m):
            for j in range(n):
                matrix[i][j] = cipher[k]
                k += 1
        steps.append(
            {
                "step": 2,
                "title": "После снятия перестановки",
                "description": "Получен промежуточный текст после лозунговой замены при шифровании.",
                "text": mid,
                "visualization": {
                    **_trans_visualization(m, n, matrix, spiral),
                },
            }
        )
        out = substitute_decrypt(mid, sub_key, RUSSIAN_ALPHABET)
        steps.append(
            {
                "step": 3,
                "title": "Исходный текст",
                "description": "Применена обратная замена по ключу.",
                "text": out,
                "visualization": _sub_visualization(sub_key),
            }
        )
        return steps, out

    if mode == "trans_then_sub":
        # Зашифрование: перестановка → замена. Расшифрование: сначала замена, потом перестановка.
        if not sub_key:
            raise ValueError("Ключ не может быть пустым")
        if m is None or n is None:
            raise ValueError("Укажите размер матрицы: m и n")
        if m < 2 or n < 2:
            raise ValueError("Размер матрицы слишком маленький (нужно хотя бы 2×2)")
        cipher = _normalize_sub_text(text)
        if not cipher:
            raise ValueError("В тексте нет букв русского алфавита")
        steps.append(
            {
                "step": 1,
                "title": "Введённый шифртекст",
                "description": "Сначала снимаем замену, потом — перестановку.",
                "text": cipher,
                "visualization": {"type": "cipher_input"},
            }
        )
        mid = substitute_decrypt(cipher, sub_key, RUSSIAN_ALPHABET)
        steps.append(
            {
                "step": 2,
                "title": "После снятия замены",
                "description": "Промежуточный текст для таблицы перестановки.",
                "text": mid,
                "visualization": _sub_visualization(sub_key),
            }
        )
        if len(mid) != m * n:
            raise ValueError(
                f"После расшифровки замены длина должна быть {m * n} (сейчас {len(mid)})"
            )
        spiral = get_spiral_indices(m, n)
        plain = transposition_decrypt(mid, m, n)
        matrix = [["" for _ in range(n)] for _ in range(m)]
        k = 0
        for i in range(m):
            for j in range(n):
                matrix[i][j] = mid[k]
                k += 1
        steps.append(
            {
                "step": 3,
                "title": "Исходный текст",
                "description": "Снята перестановка (чтение по спирали после ввода по строкам).",
                "text": plain,
                "visualization": _trans_visualization(m, n, matrix, spiral),
            }
        )
        return steps, plain

    raise ValueError(f"Неизвестный режим: {mode}")
