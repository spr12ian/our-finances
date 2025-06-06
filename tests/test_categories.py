from src.finances.categories import classify_transaction


def test_classify_transaction():
    rules = {"Rent": ["rent", "tenant"], "Interest": ["interest"]}
    assert classify_transaction("Tenant Payment", rules) == "Rent"
    assert classify_transaction("Bank Interest", rules) == "Interest"
    assert classify_transaction("Other", rules) == "Uncategorised"
