import pytest

from app.services.demo_generator import generate_transactions


def test_generator_is_reproducible_except_for_ids() -> None:
    first = generate_transactions(5, 0.2, seed=42)
    second = generate_transactions(5, 0.2, seed=42)

    assert [item.amount for item in first] == [item.amount for item in second]
    assert [item.user_id for item in first] == [item.user_id for item in second]


@pytest.mark.parametrize("count", [0, 1001])
def test_generator_rejects_invalid_count(count: int) -> None:
    with pytest.raises(ValueError):
        generate_transactions(count=count)

