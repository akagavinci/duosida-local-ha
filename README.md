# Duosida Local — Home Assistant integration

Local (LAN) control of Duosida EV wallbox chargers over TCP port 9988. No cloud.

Wraps the [duosida-local](https://github.com/matiaskunin/duosida-local) protocol
library by Matias Kunin (GPL-3.0, vendored under `vendor/`).

## Entities
- Sensors: charger state, power, current, session energy, total energy, temperature
- Number: max charging current (6–32 A) — supports live adjustment mid-session
- Buttons: start charging, stop charging

## Install
HACS → custom repository → this repo (integration) → install → restart →
Settings → Devices & Services → Add Integration → "Duosida Local" → wallbox IP.

## Notes
- The wallbox accepts a single TCP session; the integration holds it and
  reconnects with backoff if lost. Avoid concurrent use of other local clients.
- Tested on SES-32 (single-phase 7.2 kW, firmware V2.5).

License: GPL-3.0 (inherited from the vendored library).
