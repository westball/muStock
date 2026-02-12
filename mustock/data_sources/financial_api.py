from __future__ import annotations

import pandas as pd
import yfinance as yf


class FinancialDataClient:
    """Extract inventory and capex proxies from quarterly financial statements."""

    def get_inventory_and_capex(self, ticker: str) -> pd.DataFrame:
        tk = yf.Ticker(ticker)
        balance_sheet = tk.quarterly_balance_sheet.T
        cashflow = tk.quarterly_cashflow.T

        if balance_sheet.empty or cashflow.empty:
            raise ValueError(f"Unable to load financial statements for {ticker}")

        inventory_col = self._pick_first(balance_sheet, ["Inventory", "Inventory And Supplies"])
        capex_col = self._pick_first(cashflow, ["Capital Expenditure", "Capital Expenditures"])

        merged = pd.DataFrame(
            {
                "date": balance_sheet.index,
                "inventory": balance_sheet[inventory_col],
            }
        ).merge(
            pd.DataFrame(
                {
                    "date": cashflow.index,
                    "capex": cashflow[capex_col],
                }
            ),
            on="date",
            how="inner",
        )
        merged["capex"] = merged["capex"].abs()
        merged = merged.sort_values("date").reset_index(drop=True)
        return merged

    @staticmethod
    def _pick_first(frame: pd.DataFrame, options: list[str]) -> str:
        for option in options:
            if option in frame.columns:
                return option
        raise KeyError(f"None of the expected fields found: {options}")
