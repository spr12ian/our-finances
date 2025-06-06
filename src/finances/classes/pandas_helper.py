from typing import Any

import pandas as pd


class PandasHelper:
    def pd(self):
        return pd

    def header_to_dataframe(self, values: Any):
        # Create a DataFrame
        columns = values
        return pd.DataFrame(columns=columns)

    def infer_dtype(self, series):
        return pd.api.types.infer_dtype(series)

    def worksheet_values_to_dataframe(self, worksheet_values):
        # Create a DataFrame
        columns = worksheet_values[0]  # Assume the first row contains headers
        rows = worksheet_values[1:]  # Remaining rows are the data
        return pd.DataFrame(rows, columns=columns)
