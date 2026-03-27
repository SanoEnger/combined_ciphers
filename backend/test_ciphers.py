"""Быстрые проверки шифров (запуск: python test_ciphers.py из папки backend)."""

from ciphers.combined_steps import get_decryption_steps, get_encryption_steps
from ciphers.substitution import RUSSIAN_ALPHABET, substitute_decrypt, substitute_encrypt
from ciphers.transposition import transposition_decrypt, transposition_encrypt


def test_trans_roundtrip():
    for m, n in [(3, 3), (4, 3), (2, 5)]:
        t = "А" * (m * n)
        ct, padded, _pc = transposition_encrypt(t, m, n)
        dec = transposition_decrypt(ct, m, n)
        assert dec == padded, (m, n)


def test_sub_roundtrip():
    k = "КОД"
    plain = "ПРИВЕТМИР"
    c = substitute_encrypt(plain, k, RUSSIAN_ALPHABET)
    d = substitute_decrypt(c, k, RUSSIAN_ALPHABET)
    assert d == plain


def test_combined():
    k = "КОД"
    plain = "ПРИВЕТМИР"
    _, fin = get_encryption_steps(plain, "sub_then_trans", sub_key=k, m=3, n=3)
    _, back = get_decryption_steps(fin, "sub_then_trans", sub_key=k, m=3, n=3)
    assert back == plain

    _, fin2 = get_encryption_steps(plain, "trans_then_sub", sub_key=k, m=3, n=3)
    _, back2 = get_decryption_steps(fin2, "trans_then_sub", sub_key=k, m=3, n=3)
    assert back2 == plain


if __name__ == "__main__":
    test_trans_roundtrip()
    test_sub_roundtrip()
    test_combined()
    print("ok")
