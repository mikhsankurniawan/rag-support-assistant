from app.services.ingestion import _hash_text


def test_hash_text_returns_same_hash_for_same_content():
    text = "Support agents should escalate payment failures."

    hash_1 = _hash_text(text)
    hash_2 = _hash_text(text)

    assert hash_1 == hash_2


def test_hash_text_ignores_extra_blank_lines_and_outer_spaces():
    text_1 = """
    Support agents should escalate payment failures.

    Missing transaction records require engineering review.
    """

    text_2 = "Support agents should escalate payment failures.\nMissing transaction records require engineering review."

    assert _hash_text(text_1) == _hash_text(text_2)


def test_hash_text_returns_different_hash_for_different_content():
    text_1 = "Support agents should escalate payment failures."
    text_2 = "Support agents should escalate password reset issues."

    assert _hash_text(text_1) != _hash_text(text_2)