from decimal import Decimal

import pandas as pd


def d(string) -> Decimal:
    return Decimal(string)


print(d("5.6") * d("2.1"))
# Sample data
data = {
    "A": [Decimal("1.1"), Decimal("2.2"), Decimal("3.3")],
    "B": [Decimal("4.4"), Decimal("5.5"), Decimal("6.6")],
}

# Creating the DataFrame
df = pd.DataFrame(data)

print(df)
