# Security

This repository must not contain:

- exchange credentials or API keys;
- model-provider credentials;
- private endpoints or tokens;
- live or paper trading configuration;
- raw market datasets;
- runtime logs containing prompts or provider envelopes;
- production state, orders, positions, or account information.

TDH is research-and-backtest-only. Report accidental secret exposure privately
to the repository owner and rotate the affected credential before publishing a
fix.
