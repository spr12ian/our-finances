from typing import Any

from pandas import DataFrame, api


class PandasHelper:

    def header_to_dataframe(self, values: Any) -> DataFrame:
        # Create a DataFrame
        columns = values
        return DataFrame(columns=columns)

    def infer_dtype(self, series: bool) -> str:
        return api.types.infer_dtype(series)

    def worksheet_values_to_dataframe(self, worksheet_values: list[Any]) -> DataFrame:
        # Create a DataFrame
        columns = worksheet_values[0]  # Assume the first row contains headers
        rows = worksheet_values[1:]  # Remaining rows are the data
        return DataFrame(rows, columns=columns)
