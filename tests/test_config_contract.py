from pathlib import Path

import yaml


CONFIG = Path(__file__).resolve().parents[1] / "configs" / "tdh_v1_5m.yaml"


def test_single_exchange_config_satisfies_phoenix_ledger_contract() -> None:
    config = yaml.safe_load(CONFIG.read_text())
    strategy = config["strategy"]

    assert strategy["exchange1_notional_usd"] > 0
    assert strategy["exchange2_notional_usd"] == 0
    assert strategy["exchange2_margin_usd"] == 0

    # Phoenix currently computes liquidation diagnostics for both exchange
    # columns even when EX2 carries no position. Both values must therefore be
    # valid inputs to the diagnostic formula.
    assert strategy["exchange1_leverage"] > 0
    assert strategy["exchange2_leverage"] > 0
    assert 0 <= strategy["exchange1_mmr"] < 1
    assert 0 <= strategy["exchange2_mmr"] < 1


def test_fixed_r_geometry_is_frozen() -> None:
    strategy = yaml.safe_load(CONFIG.read_text())["strategy"]

    assert strategy["sl_mode"] == "pct"
    assert strategy["rr_ratio"] == 2.0
    assert strategy["worst_case_intrabar"] is True
