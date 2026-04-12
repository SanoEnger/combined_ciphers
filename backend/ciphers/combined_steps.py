"""Пошаговые сценарии шифрования и расшифрования для API обучения."""

from __future__ import annotations

from typing import Any

from .substitution import RUSSIAN_ALPHABET, create_substitution_alphabets, substitute_decrypt, substitute_encrypt
from .transposition import PAD_CHAR, get_spiral_indices, transposition_decrypt, transposition_encrypt, calculate_matrix_size


def _normalize_text(text: str) -> str:
    """Нормализация текста - только буквы русского алфавита в верхнем регистре"""
    return "".join(ch.upper() for ch in text if ch.upper() in RUSSIAN_ALPHABET)


def _strip_padding(text: str, pad_char: str = PAD_CHAR) -> str:
    """Удаляет паддинг-символы с конца строки"""
    return text.rstrip(pad_char)


def _sub_visualization(key: str, period: int) -> dict[str, Any]:
    """Визуализация таблицы замены"""
    shifts = create_substitution_alphabets(key, RUSSIAN_ALPHABET, period)
    rows = []
    for i in range(period):
        rows.append({
            "position_in_period": i + 1,
            "shifted_alphabet": list(shifts[i]),
        })
    return {
        "type": "substitution",
        "keyword": key.upper(),
        "period": period,
        "base_alphabet": list(RUSSIAN_ALPHABET),
        "rows": rows,
    }


def _trans_visualization(m: int, n: int, matrix: list[list[str]], spiral: list[tuple[int, int]], read_method: str = "row") -> dict[str, Any]:
    """Визуализация матрицы перестановки"""
    method_names = {
        "row": "Построчно слева направо",
        "snake_left_right": "Змейкой (← →)",
        "snake_right_left": "Змейкой (→ ←)",
        "snake_top_down": "Змейкой по столбцам (↓ ↑)",
        "snake_bottom_up": "Змейкой по столбцам снизу вверх",
    }
    return {
        "type": "transposition",
        "m": m,
        "n": n,
        "matrix": matrix,
        "spiral_order": [{"row": r, "col": c} for r, c in spiral],
        "read_method": read_method,
        "read_description": method_names.get(read_method, "Построчно слева направо"),
    }


def get_encryption_steps(
    text: str,
    mode: str,
    sub_key: str | None = None,
    period: int | None = None,
    m: int | None = None,
    n: int | None = None,
    read_method: str = "row",
) -> tuple[list[dict[str, Any]], str]:
    """
    Возвращает (список шагов, финальный текст) для шифрования.
    """
    steps: list[dict[str, Any]] = []
    sub_key = (sub_key or "").strip().upper()
    
    # Нормализуем входной текст
    normalized_text = _normalize_text(text)
    if not normalized_text:
        raise ValueError("В тексте нет букв русского алфавита")

    # ==================== ТОЛЬКО ЗАМЕНА ====================
    if mode == "substitution":
        if not sub_key:
            raise ValueError("Лозунг (sub_key) не может быть пустым")
        if period is None or period < 1:
            raise ValueError("Период (period) должен быть указан и быть положительным числом")
        
        steps.append({
            "step": 1,
            "title": "Исходный текст",
            "description": "Текст после нормализации (только буквы русского алфавита в верхнем регистре)",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        
        steps.append({
            "step": 2,
            "title": "Таблица замены",
            "description": f"Создано {period} алфавитов замены на основе лозунга «{sub_key}»",
            "source_text": None,
            "result_text": None,
            "visualization": _sub_visualization(sub_key, period)
        })
        
        positions = []
        for i, ch in enumerate(normalized_text):
            alphabet_num = (i % period) + 1
            positions.append({
                "position": i + 1,
                "char": ch,
                "alphabet_number": alphabet_num,
                "alphabet_index": i % period
            })
        
        steps.append({
            "step": 3,
            "title": "Определение алфавита для каждой буквы",
            "description": f"Каждая буква шифруется с использованием алфавита №(позиция mod {period} + 1)",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {
                "type": "position_mapping",
                "period": period,
                "positions": positions
            }
        })
        
        shifts = create_substitution_alphabets(sub_key, RUSSIAN_ALPHABET, period)
        current_text = list(normalized_text)
        
        for i, ch in enumerate(normalized_text):
            idx = RUSSIAN_ALPHABET.index(ch)
            alphabet_num = i % period
            cipher_alph = shifts[alphabet_num]
            new_ch = cipher_alph[idx]
            
            temp_text = current_text.copy()
            temp_text[i] = new_ch
            
            steps.append({
                "step": 4 + i,
                "title": f"Замена буквы {i+1} из {len(normalized_text)}",
                "description": f"Позиция {i+1}: буква '{ch}' (позиция {idx+1} в алфавите) → используется алфавит №{alphabet_num + 1} → заменяется на '{new_ch}'",
                "source_text": "".join(temp_text),
                "result_text": None,
                "visualization": {
                    "type": "single_substitution",
                    "position": i + 1,
                    "original_char": ch,
                    "original_index": idx + 1,
                    "alphabet_number": alphabet_num + 1,
                    "alphabet": list(cipher_alph),
                    "new_char": new_ch,
                    "new_index": cipher_alph.index(new_ch) + 1,
                    "current_text": "".join(temp_text)
                }
            })
            
            current_text[i] = new_ch
        
        encrypted = "".join(current_text)
        
        steps.append({
            "step": 4 + len(normalized_text),
            "title": "Результат шифрования заменой",
            "description": f"Текст зашифрован с использованием лозунга «{sub_key}» и периода {period}",
            "source_text": encrypted,
            "result_text": encrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, encrypted

    # ==================== ТОЛЬКО ПЕРЕСТАНОВКА (шифрование) ====================
    if mode == "transposition":
        if m is None or n is None:
            m, n = calculate_matrix_size(len(normalized_text))
        if m is None or n is None:
            raise ValueError("Не удалось определить размер матрицы")
        if m < 1 or n < 1:
            raise ValueError("Размер матрицы должен быть положительным")
            
        cells = m * n
        original_text = normalized_text
        if len(original_text) > cells:
            original_text = original_text[:cells]
        
        steps.append({
            "step": 1,
            "title": "Исходный текст",
            "description": f"Текст для заполнения матрицы {m}×{n}",
            "source_text": original_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        
        spiral = get_spiral_indices(m, n)
        empty_matrix = [["" for _ in range(n)] for _ in range(m)]
        
        steps.append({
            "step": 2,
            "title": "Пустая матрица",
            "description": f"Создана пустая матрица размером {m}×{n}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "empty_matrix",
                "m": m,
                "n": n,
                "matrix": empty_matrix
            }
        })
        
        steps.append({
            "step": 3,
            "title": "Порядок заполнения матрицы",
            "description": "Заполнение матрицы по спирали от центра против часовой стрелки",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "spiral_order",
                "m": m,
                "n": n,
                "spiral_order": [{"row": r, "col": c, "index": i, "order": i+1} for i, (r, c) in enumerate(spiral)]
            }
        })
        
        encrypted, padded, pad_count = transposition_encrypt(original_text, m, n, pad_char=PAD_CHAR, read_method=read_method)
        
        matrix = [["" for _ in range(n)] for _ in range(m)]
        
        for step_idx, (r, c) in enumerate(spiral):
            if step_idx < len(padded):
                matrix[r][c] = padded[step_idx]
                steps.append({
                    "step": 4 + step_idx,
                    "title": f"Заполнение ячейки {step_idx + 1} из {len(spiral)}",
                    "description": f"Позиция {step_idx + 1} по спирали: строка {r}, столбец {c} → символ '{padded[step_idx]}'",
                    "source_text": None,
                    "result_text": None,
                    "visualization": {
                        "type": "matrix_fill_step",
                        "step": step_idx + 1,
                        "row": r,
                        "col": c,
                        "char": padded[step_idx],
                        "matrix": [row[:] for row in matrix]
                    }
                })
        
        steps.append({
            "step": 4 + len(spiral),
            "title": "Заполненная матрица",
            "description": f"Текст записан в матрицу по спирали. Добавлено символов '{PAD_CHAR}': {pad_count}",
            "source_text": None,
            "result_text": None,
            "visualization": _trans_visualization(m, n, matrix, spiral, read_method)
        })
        
        steps.append({
            "step": 5 + len(spiral),
            "title": f"Чтение матрицы: {_trans_visualization(m, n, matrix, spiral, read_method)['read_description']}",
            "description": "Матрица читается выбранным способом",
            "source_text": encrypted,
            "result_text": None,
            "visualization": {
                "type": "reading_order",
                "read_method": read_method,
                "read_description": _trans_visualization(m, n, matrix, spiral, read_method)['read_description']
            }
        })
        
        steps.append({
            "step": 6 + len(spiral),
            "title": "Результат шифрования перестановкой",
            "description": f"Текст записан в матрицу по спирали от центра, затем прочитан. Добавлено символов '{PAD_CHAR}': {pad_count}",
            "source_text": encrypted,
            "result_text": encrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, encrypted

    # ==================== ЗАМЕНА → ПЕРЕСТАНОВКА (шифрование) ====================
    if mode == "sub_then_trans":
        if not sub_key:
            raise ValueError("Лозунг (sub_key) не может быть пустым")
        if period is None or period < 1:
            raise ValueError("Период (period) должен быть указан и быть положительным числом")
        
        step_counter = 1
        
        steps.append({
            "step": step_counter,
            "title": "Исходный текст",
            "description": "Текст перед шифрованием",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Таблица замены (лозунговая замена)",
            "description": f"Создано {period} алфавитов замены на основе лозунга «{sub_key}»",
            "source_text": None,
            "result_text": None,
            "visualization": _sub_visualization(sub_key, period)
        })
        step_counter += 1
        
        positions = []
        for i, ch in enumerate(normalized_text):
            alphabet_num = (i % period) + 1
            positions.append({
                "position": i + 1,
                "char": ch,
                "alphabet_number": alphabet_num,
                "alphabet_index": i % period
            })
        
        steps.append({
            "step": step_counter,
            "title": "Определение алфавита для каждой буквы",
            "description": f"Каждая буква шифруется с использованием алфавита №(позиция mod {period} + 1)",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {
                "type": "position_mapping",
                "period": period,
                "positions": positions
            }
        })
        step_counter += 1
        
        shifts = create_substitution_alphabets(sub_key, RUSSIAN_ALPHABET, period)
        current_text = list(normalized_text)
        
        for i, ch in enumerate(normalized_text):
            idx = RUSSIAN_ALPHABET.index(ch)
            alphabet_num = i % period
            cipher_alph = shifts[alphabet_num]
            new_ch = cipher_alph[idx]
            
            temp_text = current_text.copy()
            temp_text[i] = new_ch
            
            steps.append({
                "step": step_counter,
                "title": f"Замена буквы {i+1} из {len(normalized_text)}",
                "description": f"Позиция {i+1}: буква '{ch}' → алфавит №{alphabet_num + 1} → '{new_ch}'",
                "source_text": "".join(temp_text),
                "result_text": None,
                "visualization": {
                    "type": "single_substitution",
                    "position": i + 1,
                    "original_char": ch,
                    "alphabet_number": alphabet_num + 1,
                    "new_char": new_ch,
                    "current_text": "".join(temp_text)
                }
            })
            
            current_text[i] = new_ch
            step_counter += 1
        
        after_sub = "".join(current_text)
        
        steps.append({
            "step": step_counter,
            "title": "Результат замены",
            "description": f"Текст после шифрования заменой",
            "source_text": after_sub,
            "result_text": after_sub,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        if m is None or n is None:
            m, n = calculate_matrix_size(len(after_sub))
        
        cells = m * n
        if len(after_sub) > cells:
            after_sub = after_sub[:cells]
        
        steps.append({
            "step": step_counter,
            "title": "Подготовка к перестановке",
            "description": f"Текст обрезан до размера матрицы {m}×{n} = {cells} символов",
            "source_text": after_sub,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        spiral = get_spiral_indices(m, n)
        empty_matrix = [["" for _ in range(n)] for _ in range(m)]
        
        steps.append({
            "step": step_counter,
            "title": "Пустая матрица для перестановки",
            "description": f"Создана пустая матрица размером {m}×{n}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "empty_matrix",
                "m": m,
                "n": n,
                "matrix": empty_matrix
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Порядок заполнения матрицы",
            "description": "Заполнение матрицы по спирали от центра против часовой стрелки",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "spiral_order",
                "m": m,
                "n": n,
                "spiral_order": [{"row": r, "col": c, "index": i, "order": i+1} for i, (r, c) in enumerate(spiral)]
            }
        })
        step_counter += 1
        
        encrypted, padded, pad_count = transposition_encrypt(after_sub, m, n, pad_char=PAD_CHAR, read_method=read_method)
        
        matrix = [["" for _ in range(n)] for _ in range(m)]
        
        for step_idx, (r, c) in enumerate(spiral):
            if step_idx < len(padded):
                matrix[r][c] = padded[step_idx]
                steps.append({
                    "step": step_counter,
                    "title": f"Заполнение ячейки {step_idx + 1} из {len(spiral)}",
                    "description": f"Позиция {step_idx + 1} по спирали: строка {r}, столбец {c} → символ '{padded[step_idx]}'",
                    "source_text": None,
                    "result_text": None,
                    "visualization": {
                        "type": "matrix_fill_step",
                        "step": step_idx + 1,
                        "row": r,
                        "col": c,
                        "char": padded[step_idx],
                        "matrix": [row[:] for row in matrix]
                    }
                })
                step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Заполненная матрица",
            "description": f"Текст записан в матрицу. Добавлено символов '{PAD_CHAR}': {pad_count}",
            "source_text": None,
            "result_text": None,
            "visualization": _trans_visualization(m, n, matrix, spiral, read_method)
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": f"Чтение матрицы",
            "description": f"Матрица читается способом: {_trans_visualization(m, n, matrix, spiral, read_method)['read_description']}",
            "source_text": encrypted,
            "result_text": None,
            "visualization": {
                "type": "reading_order",
                "read_method": read_method,
                "read_description": _trans_visualization(m, n, matrix, spiral, read_method)['read_description']
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Финальный результат",
            "description": "Комбинированное шифрование: Замена → Перестановка",
            "source_text": encrypted,
            "result_text": encrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, encrypted

    # ==================== ПЕРЕСТАНОВКА → ЗАМЕНА (шифрование) ====================
    if mode == "trans_then_sub":
        if not sub_key:
            raise ValueError("Лозунг (sub_key) не может быть пустым")
        if period is None or period < 1:
            raise ValueError("Период (period) должен быть указан и быть положительным числом")
        
        if m is None or n is None:
            m, n = calculate_matrix_size(len(normalized_text))
        if m is None or n is None:
            raise ValueError("Не удалось определить размер матрицы")
        
        step_counter = 1
        
        steps.append({
            "step": step_counter,
            "title": "Исходный текст",
            "description": "Текст перед шифрованием",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        cells = m * n
        if len(normalized_text) > cells:
            truncated = normalized_text[:cells]
        else:
            truncated = normalized_text
        
        steps.append({
            "step": step_counter,
            "title": "Подготовка к перестановке",
            "description": f"Текст обрезан до размера матрицы {m}×{n} = {cells} символов",
            "source_text": truncated,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        spiral = get_spiral_indices(m, n)
        empty_matrix = [["" for _ in range(n)] for _ in range(m)]
        
        steps.append({
            "step": step_counter,
            "title": "Пустая матрица для перестановки",
            "description": f"Создана пустая матрица размером {m}×{n}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "empty_matrix",
                "m": m,
                "n": n,
                "matrix": empty_matrix
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Порядок заполнения матрицы",
            "description": "Заполнение матрицы по спирали от центра против часовой стрелки",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "spiral_order",
                "m": m,
                "n": n,
                "spiral_order": [{"row": r, "col": c, "index": i, "order": i+1} for i, (r, c) in enumerate(spiral)]
            }
        })
        step_counter += 1
        
        after_trans, padded, pad_count = transposition_encrypt(truncated, m, n, pad_char=PAD_CHAR, read_method=read_method)
        
        matrix = [["" for _ in range(n)] for _ in range(m)]
        
        for step_idx, (r, c) in enumerate(spiral):
            if step_idx < len(padded):
                matrix[r][c] = padded[step_idx]
                steps.append({
                    "step": step_counter,
                    "title": f"Заполнение ячейки {step_idx + 1} из {len(spiral)}",
                    "description": f"Позиция {step_idx + 1} по спирали: строка {r}, столбец {c} → символ '{padded[step_idx]}'",
                    "source_text": None,
                    "result_text": None,
                    "visualization": {
                        "type": "matrix_fill_step",
                        "step": step_idx + 1,
                        "row": r,
                        "col": c,
                        "char": padded[step_idx],
                        "matrix": [row[:] for row in matrix]
                    }
                })
                step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Заполненная матрица",
            "description": f"Текст записан в матрицу. Добавлено символов '{PAD_CHAR}': {pad_count}",
            "source_text": None,
            "result_text": None,
            "visualization": _trans_visualization(m, n, matrix, spiral, read_method)
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": f"Чтение матрицы",
            "description": f"Матрица читается способом: {_trans_visualization(m, n, matrix, spiral, read_method)['read_description']}",
            "source_text": after_trans,
            "result_text": None,
            "visualization": {
                "type": "reading_order",
                "read_method": read_method,
                "read_description": _trans_visualization(m, n, matrix, spiral, read_method)['read_description']
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Результат перестановки",
            "description": f"Текст после перестановки",
            "source_text": after_trans,
            "result_text": after_trans,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Таблица замены",
            "description": f"Создано {period} алфавитов замены на основе лозунга «{sub_key}»",
            "source_text": None,
            "result_text": None,
            "visualization": _sub_visualization(sub_key, period)
        })
        step_counter += 1
        
        positions = []
        for i, ch in enumerate(after_trans):
            alphabet_num = (i % period) + 1
            positions.append({
                "position": i + 1,
                "char": ch,
                "alphabet_number": alphabet_num,
                "alphabet_index": i % period
            })
        
        steps.append({
            "step": step_counter,
            "title": "Определение алфавита для каждой буквы",
            "description": f"Каждая буква шифруется с использованием алфавита №(позиция mod {period} + 1)",
            "source_text": after_trans,
            "result_text": None,
            "visualization": {
                "type": "position_mapping",
                "period": period,
                "positions": positions
            }
        })
        step_counter += 1
        
        shifts = create_substitution_alphabets(sub_key, RUSSIAN_ALPHABET, period)
        current_text = list(after_trans)
        
        for i, ch in enumerate(after_trans):
            if ch in RUSSIAN_ALPHABET:
                idx = RUSSIAN_ALPHABET.index(ch)
                alphabet_num = i % period
                cipher_alph = shifts[alphabet_num]
                new_ch = cipher_alph[idx]
                
                temp_text = current_text.copy()
                temp_text[i] = new_ch
                
                steps.append({
                    "step": step_counter,
                    "title": f"Замена буквы {i+1} из {len(after_trans)}",
                    "description": f"Позиция {i+1}: буква '{ch}' → алфавит №{alphabet_num + 1} → '{new_ch}'",
                    "source_text": "".join(temp_text),
                    "result_text": None,
                    "visualization": {
                        "type": "single_substitution",
                        "position": i + 1,
                        "original_char": ch,
                        "alphabet_number": alphabet_num + 1,
                        "new_char": new_ch,
                        "current_text": "".join(temp_text)
                    }
                })
                
                current_text[i] = new_ch
            else:
                temp_text = current_text.copy()
                steps.append({
                    "step": step_counter,
                    "title": f"Пропуск символа {i+1}",
                    "description": f"Символ '{ch}' не является буквой русского алфавита",
                    "source_text": "".join(temp_text),
                    "result_text": None,
                    "visualization": {
                        "type": "skip_substitution",
                        "position": i + 1,
                        "char": ch
                    }
                })
            
            step_counter += 1
        
        encrypted = "".join(current_text)
        
        steps.append({
            "step": step_counter,
            "title": "Финальный результат",
            "description": "Комбинированное шифрование: Перестановка → Замена",
            "source_text": encrypted,
            "result_text": encrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, encrypted

    raise ValueError(f"Неизвестный режим: {mode}")


def get_decryption_steps(
    text: str,
    mode: str,
    sub_key: str | None = None,
    period: int | None = None,
    m: int | None = None,
    n: int | None = None,
    read_method: str = "row",
) -> tuple[list[dict[str, Any]], str]:
    """
    Расшифрование - обратный порядок операций с детальными шагами.
    """
    steps: list[dict[str, Any]] = []
    sub_key = (sub_key or "").strip().upper()
    
    normalized_text = _normalize_text(text)
    if not normalized_text:
        raise ValueError("В тексте нет букв русского алфавита")

    # ==================== ТОЛЬКО ЗАМЕНА ====================
    if mode == "substitution":
        if not sub_key:
            raise ValueError("Лозунг (sub_key) не может быть пустым")
        if period is None or period < 1:
            raise ValueError("Период (period) должен быть указан и быть положительным числом")
        
        step_counter = 1
        
        steps.append({
            "step": step_counter,
            "title": "Шифртекст",
            "description": "Текст для расшифровки",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Таблица замены",
            "description": f"Создано {period} алфавитов замены на основе лозунга «{sub_key}»",
            "source_text": None,
            "result_text": None,
            "visualization": _sub_visualization(sub_key, period)
        })
        step_counter += 1
        
        positions = []
        for i, ch in enumerate(normalized_text):
            alphabet_num = (i % period) + 1
            positions.append({
                "position": i + 1,
                "char": ch,
                "alphabet_number": alphabet_num,
                "alphabet_index": i % period
            })
        
        steps.append({
            "step": step_counter,
            "title": "Определение алфавита для каждой буквы",
            "description": f"Каждая буква расшифровывается с использованием алфавита №(позиция mod {period} + 1)",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {
                "type": "position_mapping",
                "period": period,
                "positions": positions
            }
        })
        step_counter += 1
        
        shifts = create_substitution_alphabets(sub_key, RUSSIAN_ALPHABET, period)
        current_text = list(normalized_text)
        
        for i, ch in enumerate(normalized_text):
            shifted = shifts[i % period]
            idx = shifted.index(ch)
            original_char = RUSSIAN_ALPHABET[idx]
            
            temp_text = current_text.copy()
            temp_text[i] = original_char
            
            steps.append({
                "step": step_counter,
                "title": f"Расшифровка буквы {i+1} из {len(normalized_text)}",
                "description": f"Позиция {i+1}: буква '{ch}' в алфавите №{(i % period) + 1} соответствует букве '{original_char}'",
                "source_text": "".join(temp_text),
                "result_text": None,
                "visualization": {
                    "type": "single_decryption",
                    "position": i + 1,
                    "encrypted_char": ch,
                    "alphabet_number": (i % period) + 1,
                    "original_char": original_char,
                    "current_text": "".join(temp_text)
                }
            })
            
            current_text[i] = original_char
            step_counter += 1
        
        decrypted = "".join(current_text)
        
        steps.append({
            "step": step_counter,
            "title": "Результат расшифровки",
            "description": f"Текст расшифрован с использованием лозунга «{sub_key}» и периода {period}",
            "source_text": decrypted,
            "result_text": decrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, decrypted

    # ==================== ТОЛЬКО ПЕРЕСТАНОВКА (расшифрование) ====================
    if mode == "transposition":
        if m is None or n is None:
            raise ValueError("Для расшифрования укажите размер матрицы m и n")
        cells = m * n
        if len(normalized_text) != cells:
            raise ValueError(f"Длина шифртекста должна быть {cells} символов")
        
        step_counter = 1
        
        steps.append({
            "step": step_counter,
            "title": "Шифртекст",
            "description": f"Текст для расшифровки (длина {cells} символов)",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        spiral = get_spiral_indices(m, n)
        empty_matrix = [["" for _ in range(n)] for _ in range(m)]
        
        steps.append({
            "step": step_counter,
            "title": "Пустая матрица",
            "description": f"Создана пустая матрица размером {m}×{n}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "empty_matrix",
                "m": m,
                "n": n,
                "matrix": empty_matrix
            }
        })
        step_counter += 1
        
        # Определяем порядок индексов для записи шифртекста (обратный методу чтения)
        if read_method == "row":
            indices = [(i, j) for i in range(m) for j in range(n)]
        elif read_method == "snake_left_right":
            indices = []
            for i in range(m):
                if i % 2 == 0:
                    for j in range(n):
                        indices.append((i, j))
                else:
                    for j in range(n-1, -1, -1):
                        indices.append((i, j))
        elif read_method == "snake_right_left":
            indices = []
            for i in range(m):
                if i % 2 == 0:
                    for j in range(n-1, -1, -1):
                        indices.append((i, j))
                else:
                    for j in range(n):
                        indices.append((i, j))
        elif read_method == "snake_top_down":
            indices = []
            for j in range(n):
                if j % 2 == 0:
                    for i in range(m):
                        indices.append((i, j))
                else:
                    for i in range(m-1, -1, -1):
                        indices.append((i, j))
        elif read_method == "snake_bottom_up":
            indices = []
            for j in range(n-1, -1, -1):
                if (n-1 - j) % 2 == 0:
                    for i in range(m):
                        indices.append((i, j))
                else:
                    for i in range(m-1, -1, -1):
                        indices.append((i, j))
        else:
            indices = [(i, j) for i in range(m) for j in range(n)]
        
        steps.append({
            "step": step_counter,
            "title": f"Запись шифртекста в матрицу",
            "description": f"Шифртекст записывается в матрицу способом: {_trans_visualization(m, n, empty_matrix, spiral, read_method)['read_description']}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "reading_order",
                "read_method": read_method,
                "read_description": _trans_visualization(m, n, empty_matrix, spiral, read_method)['read_description']
            }
        })
        step_counter += 1
        
        matrix = [["" for _ in range(n)] for _ in range(m)]
        
        for idx, (r, c) in enumerate(indices):
            if idx < len(normalized_text):
                matrix[r][c] = normalized_text[idx]
                steps.append({
                    "step": step_counter,
                    "title": f"Запись символа {idx+1} из {len(normalized_text)}",
                    "description": f"Символ '{normalized_text[idx]}' записывается в позицию ({r}, {c})",
                    "source_text": None,
                    "result_text": None,
                    "visualization": {
                        "type": "matrix_fill_step",
                        "step": idx + 1,
                        "row": r,
                        "col": c,
                        "char": normalized_text[idx],
                        "matrix": [row[:] for row in matrix]
                    }
                })
                step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Заполненная матрица",
            "description": "Матрица, заполненная шифртекстом",
            "source_text": None,
            "result_text": None,
            "visualization": _trans_visualization(m, n, matrix, spiral, read_method)
        })
        step_counter += 1
        
        decrypted_with_padding = transposition_decrypt(normalized_text, m, n, read_method)
        decrypted = _strip_padding(decrypted_with_padding)
        
        steps.append({
            "step": step_counter,
            "title": "Чтение по спирали",
            "description": "Текст восстанавливается чтением матрицы по спирали от центра",
            "source_text": decrypted,
            "result_text": None,
            "visualization": {
                "type": "spiral_order",
                "m": m,
                "n": n,
                "spiral_order": [{"row": r, "col": c, "index": i, "order": i+1} for i, (r, c) in enumerate(spiral)]
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Результат расшифровки",
            "description": "Текст восстановлен чтением матрицы по спирали",
            "source_text": decrypted,
            "result_text": decrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, decrypted

    # ==================== ЗАМЕНА → ПЕРЕСТАНОВКА (расшифрование) ====================
    if mode == "sub_then_trans":
        if not sub_key:
            raise ValueError("Лозунг (sub_key) не может быть пустым")
        if period is None or period < 1:
            raise ValueError("Период (period) должен быть указан и быть положительным числом")
        if m is None or n is None:
            raise ValueError("Для расшифрования укажите размер матрицы m и n")
            
        cells = m * n
        if len(normalized_text) != cells:
            raise ValueError(f"Длина шифртекста должна быть {cells} символов")
        
        step_counter = 1
        
        steps.append({
            "step": step_counter,
            "title": "Шифртекст",
            "description": "Текст для расшифровки",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        spiral = get_spiral_indices(m, n)
        empty_matrix = [["" for _ in range(n)] for _ in range(m)]
        
        steps.append({
            "step": step_counter,
            "title": "Пустая матрица",
            "description": f"Создана пустая матрица размером {m}×{n}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "empty_matrix",
                "m": m,
                "n": n,
                "matrix": empty_matrix
            }
        })
        step_counter += 1
        
        # Индексы для записи
        if read_method == "row":
            indices = [(i, j) for i in range(m) for j in range(n)]
        elif read_method == "snake_left_right":
            indices = []
            for i in range(m):
                if i % 2 == 0:
                    for j in range(n):
                        indices.append((i, j))
                else:
                    for j in range(n-1, -1, -1):
                        indices.append((i, j))
        elif read_method == "snake_right_left":
            indices = []
            for i in range(m):
                if i % 2 == 0:
                    for j in range(n-1, -1, -1):
                        indices.append((i, j))
                else:
                    for j in range(n):
                        indices.append((i, j))
        elif read_method == "snake_top_down":
            indices = []
            for j in range(n):
                if j % 2 == 0:
                    for i in range(m):
                        indices.append((i, j))
                else:
                    for i in range(m-1, -1, -1):
                        indices.append((i, j))
        elif read_method == "snake_bottom_up":
            indices = []
            for j in range(n-1, -1, -1):
                if (n-1 - j) % 2 == 0:
                    for i in range(m):
                        indices.append((i, j))
                else:
                    for i in range(m-1, -1, -1):
                        indices.append((i, j))
        else:
            indices = [(i, j) for i in range(m) for j in range(n)]
        
        steps.append({
            "step": step_counter,
            "title": f"Запись шифртекста в матрицу",
            "description": f"Шифртекст записывается в матрицу способом: {_trans_visualization(m, n, empty_matrix, spiral, read_method)['read_description']}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "reading_order",
                "read_method": read_method,
                "read_description": _trans_visualization(m, n, empty_matrix, spiral, read_method)['read_description']
            }
        })
        step_counter += 1
        
        matrix = [["" for _ in range(n)] for _ in range(m)]
        
        for idx, (r, c) in enumerate(indices):
            if idx < len(normalized_text):
                matrix[r][c] = normalized_text[idx]
                steps.append({
                    "step": step_counter,
                    "title": f"Запись символа {idx+1} из {len(normalized_text)}",
                    "description": f"Символ '{normalized_text[idx]}' записывается в позицию ({r}, {c})",
                    "source_text": None,
                    "result_text": None,
                    "visualization": {
                        "type": "matrix_fill_step",
                        "step": idx + 1,
                        "row": r,
                        "col": c,
                        "char": normalized_text[idx],
                        "matrix": [row[:] for row in matrix]
                    }
                })
                step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Заполненная матрица",
            "description": "Матрица, заполненная шифртекстом",
            "source_text": None,
            "result_text": None,
            "visualization": _trans_visualization(m, n, matrix, spiral, read_method)
        })
        step_counter += 1
        
        decrypted_with_padding = transposition_decrypt(normalized_text, m, n, read_method)
        after_trans = _strip_padding(decrypted_with_padding)
        
        steps.append({
            "step": step_counter,
            "title": "Чтение по спирали",
            "description": "Текст восстанавливается чтением матрицы по спирали от центра",
            "source_text": after_trans,
            "result_text": None,
            "visualization": {
                "type": "spiral_order",
                "m": m,
                "n": n,
                "spiral_order": [{"row": r, "col": c, "index": i, "order": i+1} for i, (r, c) in enumerate(spiral)]
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "После снятия перестановки",
            "description": "Текст после обратной перестановки",
            "source_text": after_trans,
            "result_text": after_trans,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        # ---------- Расшифрование замены ----------
        steps.append({
            "step": step_counter,
            "title": "Таблица замены",
            "description": f"Создано {period} алфавитов замены на основе лозунга «{sub_key}»",
            "source_text": None,
            "result_text": None,
            "visualization": _sub_visualization(sub_key, period)
        })
        step_counter += 1
        
        positions = []
        for i, ch in enumerate(after_trans):
            alphabet_num = (i % period) + 1
            positions.append({
                "position": i + 1,
                "char": ch,
                "alphabet_number": alphabet_num,
                "alphabet_index": i % period
            })
        
        steps.append({
            "step": step_counter,
            "title": "Определение алфавита для каждой буквы",
            "description": f"Каждая буква расшифровывается с использованием алфавита №(позиция mod {period} + 1)",
            "source_text": after_trans,
            "result_text": None,
            "visualization": {
                "type": "position_mapping",
                "period": period,
                "positions": positions
            }
        })
        step_counter += 1
        
        shifts = create_substitution_alphabets(sub_key, RUSSIAN_ALPHABET, period)
        current_text = list(after_trans)
        
        for i, ch in enumerate(after_trans):
            shifted = shifts[i % period]
            idx = shifted.index(ch)
            original_char = RUSSIAN_ALPHABET[idx]
            
            temp_text = current_text.copy()
            temp_text[i] = original_char
            
            steps.append({
                "step": step_counter,
                "title": f"Расшифровка буквы {i+1} из {len(after_trans)}",
                "description": f"Позиция {i+1}: буква '{ch}' в алфавите №{(i % period) + 1} соответствует букве '{original_char}'",
                "source_text": "".join(temp_text),
                "result_text": None,
                "visualization": {
                    "type": "single_decryption",
                    "position": i + 1,
                    "encrypted_char": ch,
                    "alphabet_number": (i % period) + 1,
                    "original_char": original_char,
                    "current_text": "".join(temp_text)
                }
            })
            
            current_text[i] = original_char
            step_counter += 1
        
        decrypted = "".join(current_text)
        
        steps.append({
            "step": step_counter,
            "title": "Финальный результат расшифровки",
            "description": "Текст полностью расшифрован",
            "source_text": decrypted,
            "result_text": decrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, decrypted

    # ==================== ПЕРЕСТАНОВКА → ЗАМЕНА (расшифрование) ====================
    if mode == "trans_then_sub":
        if not sub_key:
            raise ValueError("Лозунг (sub_key) не может быть пустым")
        if period is None or period < 1:
            raise ValueError("Период (period) должен быть указан и быть положительным числом")
        if m is None or n is None:
            raise ValueError("Для расшифрования укажите размер матрицы m и n")
        
        step_counter = 1
        
        steps.append({
            "step": step_counter,
            "title": "Шифртекст",
            "description": "Текст для расшифровки",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        # ---------- Расшифрование замены ----------
        steps.append({
            "step": step_counter,
            "title": "Таблица замены",
            "description": f"Создано {period} алфавитов замены на основе лозунга «{sub_key}»",
            "source_text": None,
            "result_text": None,
            "visualization": _sub_visualization(sub_key, period)
        })
        step_counter += 1
        
        positions = []
        for i, ch in enumerate(normalized_text):
            alphabet_num = (i % period) + 1
            positions.append({
                "position": i + 1,
                "char": ch,
                "alphabet_number": alphabet_num,
                "alphabet_index": i % period
            })
        
        steps.append({
            "step": step_counter,
            "title": "Определение алфавита для каждой буквы",
            "description": f"Каждая буква расшифровывается с использованием алфавита №(позиция mod {period} + 1)",
            "source_text": normalized_text,
            "result_text": None,
            "visualization": {
                "type": "position_mapping",
                "period": period,
                "positions": positions
            }
        })
        step_counter += 1
        
        shifts = create_substitution_alphabets(sub_key, RUSSIAN_ALPHABET, period)
        current_text = list(normalized_text)
        
        for i, ch in enumerate(normalized_text):
            shifted = shifts[i % period]
            idx = shifted.index(ch)
            original_char = RUSSIAN_ALPHABET[idx]
            
            temp_text = current_text.copy()
            temp_text[i] = original_char
            
            steps.append({
                "step": step_counter,
                "title": f"Расшифровка буквы {i+1} из {len(normalized_text)}",
                "description": f"Позиция {i+1}: буква '{ch}' в алфавите №{(i % period) + 1} соответствует букве '{original_char}'",
                "source_text": "".join(temp_text),
                "result_text": None,
                "visualization": {
                    "type": "single_decryption",
                    "position": i + 1,
                    "encrypted_char": ch,
                    "alphabet_number": (i % period) + 1,
                    "original_char": original_char,
                    "current_text": "".join(temp_text)
                }
            })
            
            current_text[i] = original_char
            step_counter += 1
        
        after_sub = "".join(current_text)
        
        steps.append({
            "step": step_counter,
            "title": "После снятия замены",
            "description": f"Текст после обратной замены",
            "source_text": after_sub,
            "result_text": after_sub,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        # ---------- Расшифрование перестановки ----------
        cells = m * n
        if len(after_sub) != cells:
            if len(after_sub) > cells:
                after_sub = after_sub[:cells]
        
        steps.append({
            "step": step_counter,
            "title": "Подготовка к снятию перестановки",
            "description": f"Текст обрезан до размера матрицы {m}×{n} = {cells} символов",
            "source_text": after_sub,
            "result_text": None,
            "visualization": {"type": "plain"}
        })
        step_counter += 1
        
        spiral = get_spiral_indices(m, n)
        empty_matrix = [["" for _ in range(n)] for _ in range(m)]
        
        steps.append({
            "step": step_counter,
            "title": "Пустая матрица",
            "description": f"Создана пустая матрица размером {m}×{n}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "empty_matrix",
                "m": m,
                "n": n,
                "matrix": empty_matrix
            }
        })
        step_counter += 1
        
        # Индексы для записи
        if read_method == "row":
            indices = [(i, j) for i in range(m) for j in range(n)]
        elif read_method == "snake_left_right":
            indices = []
            for i in range(m):
                if i % 2 == 0:
                    for j in range(n):
                        indices.append((i, j))
                else:
                    for j in range(n-1, -1, -1):
                        indices.append((i, j))
        elif read_method == "snake_right_left":
            indices = []
            for i in range(m):
                if i % 2 == 0:
                    for j in range(n-1, -1, -1):
                        indices.append((i, j))
                else:
                    for j in range(n):
                        indices.append((i, j))
        elif read_method == "snake_top_down":
            indices = []
            for j in range(n):
                if j % 2 == 0:
                    for i in range(m):
                        indices.append((i, j))
                else:
                    for i in range(m-1, -1, -1):
                        indices.append((i, j))
        elif read_method == "snake_bottom_up":
            indices = []
            for j in range(n-1, -1, -1):
                if (n-1 - j) % 2 == 0:
                    for i in range(m):
                        indices.append((i, j))
                else:
                    for i in range(m-1, -1, -1):
                        indices.append((i, j))
        else:
            indices = [(i, j) for i in range(m) for j in range(n)]
        
        steps.append({
            "step": step_counter,
            "title": f"Запись текста в матрицу",
            "description": f"Текст записывается в матрицу способом: {_trans_visualization(m, n, empty_matrix, spiral, read_method)['read_description']}",
            "source_text": None,
            "result_text": None,
            "visualization": {
                "type": "reading_order",
                "read_method": read_method,
                "read_description": _trans_visualization(m, n, empty_matrix, spiral, read_method)['read_description']
            }
        })
        step_counter += 1
        
        matrix = [["" for _ in range(n)] for _ in range(m)]
        
        for idx, (r, c) in enumerate(indices):
            if idx < len(after_sub):
                matrix[r][c] = after_sub[idx]
                steps.append({
                    "step": step_counter,
                    "title": f"Запись символа {idx+1} из {len(after_sub)}",
                    "description": f"Символ '{after_sub[idx]}' записывается в позицию ({r}, {c})",
                    "source_text": None,
                    "result_text": None,
                    "visualization": {
                        "type": "matrix_fill_step",
                        "step": idx + 1,
                        "row": r,
                        "col": c,
                        "char": after_sub[idx],
                        "matrix": [row[:] for row in matrix]
                    }
                })
                step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Заполненная матрица",
            "description": "Матрица, заполненная текстом после снятия замены",
            "source_text": None,
            "result_text": None,
            "visualization": _trans_visualization(m, n, matrix, spiral, read_method)
        })
        step_counter += 1
        
        decrypted_with_padding = transposition_decrypt(after_sub, m, n, read_method)
        decrypted = _strip_padding(decrypted_with_padding)
        
        steps.append({
            "step": step_counter,
            "title": "Чтение по спирали",
            "description": "Текст восстанавливается чтением матрицы по спирали от центра",
            "source_text": decrypted,
            "result_text": None,
            "visualization": {
                "type": "spiral_order",
                "m": m,
                "n": n,
                "spiral_order": [{"row": r, "col": c, "index": i, "order": i+1} for i, (r, c) in enumerate(spiral)]
            }
        })
        step_counter += 1
        
        steps.append({
            "step": step_counter,
            "title": "Финальный результат расшифровки",
            "description": "Текст полностью расшифрован",
            "source_text": decrypted,
            "result_text": decrypted,
            "visualization": {"type": "plain"}
        })
        
        return steps, decrypted

    raise ValueError(f"Неизвестный режим: {mode}")