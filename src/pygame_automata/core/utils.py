import hashlib


def text_to_rule(text: str, bit_len: int) -> int:
    # hash text deterministically
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # convert hex -> int
    num = int(h, 16)

    # clamp to ruleset size
    max_rule = (1 << bit_len) - 1
    return num & max_rule
