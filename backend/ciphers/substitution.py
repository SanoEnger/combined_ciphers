"""Периодическая лозунговая замена (Джованни делла Порта)."""

from __future__ import annotations

# 33 буквы (включая Ё)
RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def _make_cipher_alphabet(keyword: str, alphabet: str) -> str:
    """Создает шифрующий алфавит на основе ключевого слова (лозунга)"""
    used: set[str] = set()
    res: list[str] = []
    keyword_upper = keyword.upper()
    for ch in keyword_upper:
        if ch not in used and ch in alphabet:
            res.append(ch)
            used.add(ch)
    for ch in alphabet:
        if ch not in used:
            res.append(ch)
    return "".join(res)


def create_substitution_alphabets(key: str, base_alphabet: str, period: int) -> list[str]:
    """
    Строит список из period шифрующих алфавитов.
    key - лозунг (слово для построения базового алфавита)
    period - количество алфавитов (длина ключа/периода)
    """
    key = (key or "").strip()
    if not key:
        raise ValueError("Лозунг не может быть пустым")
    if period < 1:
        raise ValueError("Период должен быть положительным числом")
    
    cipher_alphabet = _make_cipher_alphabet(key, base_alphabet)
    shifts: list[str] = []
    for i in range(period):
        shifted = cipher_alphabet[i:] + cipher_alphabet[:i]
        shifts.append(shifted)
    return shifts


def substitute_encrypt(text: str, key: str, alphabet: str = RUSSIAN_ALPHABET, period: int = None) -> str:
    """Шифрование текста с помощью лозунговой замены"""
    if period is None:
        period = len(key)  # для обратной совместимости
    shifts = create_substitution_alphabets(key, alphabet, period)
    period_len = len(shifts)
    clean = "".join(ch.upper() for ch in text if ch.upper() in alphabet)
    if not clean:
        return ""
    result: list[str] = []
    for i, ch in enumerate(clean):
        if ch in alphabet:
            idx = alphabet.index(ch)
            cipher_alph = shifts[i % period_len]
            result.append(cipher_alph[idx])
        else:
            result.append(ch)
    return "".join(result)


def substitute_decrypt(text: str, key: str, alphabet: str = RUSSIAN_ALPHABET, period: int = None) -> str:
    """Дешифрование текста с помощью лозунговой замены"""
    if period is None:
        period = len(key)  # для обратной совместимости
    shifts = create_substitution_alphabets(key, alphabet, period)
    period_len = len(shifts)
    # Создаем обратные отображения
    inv_maps: list[dict[str, str]] = []
    for i in range(period_len):
        shifted = shifts[i]
        inv = {shifted[j]: alphabet[j] for j in range(len(alphabet))}
        inv_maps.append(inv)
    
    clean = "".join(ch.upper() for ch in text if ch.upper() in alphabet)
    if not clean:
        return ""
    result: list[str] = []
    for i, ch in enumerate(clean):
        inv_map = inv_maps[i % period_len]
        result.append(inv_map.get(ch, ch))
    return "".join(result)