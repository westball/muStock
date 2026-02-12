import pandas as pd

from mustock.engine import CycleEngine


def test_compute_momentum_columns_exist():
    dates = pd.date_range("2025-01-01", periods=130, freq="D")
    prices = pd.DataFrame({"date": dates, "close": range(1, 131)})

    output = CycleEngine.compute_momentum(prices)

    for col in ["ret_1d", "mom_5d", "mom_21d", "mom_105d"]:
        assert col in output.columns


def test_capex_acceleration_detection():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=5, freq="Q"),
            "capex": [10, 11, 14, 20, 28],
            "inventory": [100, 103, 110, 120, 132],
        }
    )

    out = CycleEngine.detect_capex_acceleration(df)
    assert "capex_acceleration" in out.columns
    assert out["inventory_growth"].iloc[-1] > 0
