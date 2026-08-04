from __future__ import annotations

from typing import Any

import pandas as pd

from constants.column_names import GlobalIdentifiers
from constants.trades import TradeDirection
from strategies.strategy_builder.strategies.st3_phx_mean_reversion import (
    PhoenixMeanReversionStrategy,
)

from darkest_hour.signals import SignalConfig, build_entry_tokens, compute_features


class TheDarkestHourStrategy(PhoenixMeanReversionStrategy):
    """Research-only Phoenix S1 adapter for the frozen TDH v1 tournament.

    The parent supplies the audited single-exchange 2R/1R exit builder, costs,
    funding context and S1 output contract. This subclass owns entry logic only.
    """

    def _signal_config(self) -> SignalConfig:
        return SignalConfig.from_mapping(self._require_strategy_config())

    def _create_indicators(self) -> None:
        # Preserve the parent's ATR_EXIT Indicator because its inherited
        # build_strategy_output() uses it to construct each trade's stop/target.
        super()._create_indicators()
        self.indicators["tdh_features"] = compute_features(
            self.base_data,
            self._signal_config(),
        )

    def _create_signals(self) -> None:
        cfg = self._signal_config()
        tokens = build_entry_tokens(self.base_data, cfg)
        self.signals = {
            GlobalIdentifiers.ENTRY_SIGNALS: [tokens],
            GlobalIdentifiers.EXIT_SIGNALS: [],
            "tdh_entry_tokens": tokens,
            "tdh_family": cfg.family,
        }

    def _make_entry_decisions(self) -> pd.Series:
        entry = self.signals["tdh_entry_tokens"].copy().astype("string")
        self.decisions[GlobalIdentifiers.ENTRY_DECISIONS] = entry
        return entry

    def _make_exit_decisions(self) -> pd.Series:
        neutral = pd.Series(
            TradeDirection.NEUTRAL,
            index=self.base_data.index,
            dtype="string",
        )
        self.decisions[GlobalIdentifiers.EXIT_DECISIONS] = neutral
        return neutral

    def decide_live(self, snapshot: Any, bot_ctx: Any = None):
        # Kept only to satisfy the Phoenix Strategy interface. The repository
        # has no live deployment gate; inherited conversion and execution-mode
        # mapping remain deterministic if a later, separately approved paper
        # adapter invokes them.
        return super().decide_live(snapshot, bot_ctx)

