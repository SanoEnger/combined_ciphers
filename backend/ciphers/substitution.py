"""Периодическая лозунговая замена (Джованни делла Порта)."""

from __future__ import annotations

# 33 буквы по ТЗ (включая Ё)
RUSSIAN_ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def _make_cipher_alphabet(keyword: str, alphabet: str) -> str:
    used: set[str] = set()
    res: list[str] = []
    for ch in keyword.upper():
        if ch not in used and ch in alphabet:
            res.append(ch)
            used.add(ch)
    for ch in alphabet:
        if ch not in used:
            res.append(ch)
    return "".join(res)


def create_substitution_alphabets(key: str, base_alphabet: str) -> list[str]:
    """
    Строит список из period шифрующих алфавитов (сдвиги лозунгового алфавита).
    Период = длина ключа (как в примере ТЗ с ключом «КОД» — три алфавита).
    """
    key = (key or "").strip()
    if not key:
        raise ValueError("Ключ не может быть пустым")
    period = len(key)
    cipher_alphabet = _make_cipher_alphabet(key, base_alphabet)
    shifts: list[str] = []
    for i in range(period):
        shifted = cipher_alphabet[i:] + cipher_alphabet[:i]
        shifts.append(shifted)
    return shifts


def substitute_encrypt(text: str, key: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    shifts = create_substitution_alphabets(key, alphabet)
    period = len(shifts)
    clean = "".join(ch.upper() for ch in text if ch.upper() in alphabet)
    if not clean:
        return ""
    result: list[str] = []
    for i, ch in enumerate(clean):
        idx = alphabet.index(ch)
        cipher_alph = shifts[i % period]
        result.append(cipher_alph[idx])
    return "".join(result)


def substitute_decrypt(text: str, key: str, alphabet: str = RUSSIAN_ALPHABET) -> str:
    shifts = create_substitution_alphabets(key, alphabet)
    period = len(shifts)
    inv_maps: list[dict[str, str]] = []
    for i in range(period):
        shifted = shifts[i]
        inv = {c: alphabet[j] for j, c in enumerate(shifted)}
        inv_maps.append(inv)
    clean = "".join(ch.upper() for ch in text if ch.upper() in alphabet)
    if not clean:
        return ""
    result: list[str] = []
    for i, ch in enumerate(clean):
        inv_map = inv_maps[i % period]
        result.append(inv_map.get(ch, "?"))
    return "".join(result)
