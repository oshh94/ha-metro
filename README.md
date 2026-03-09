# Copenhagen Metro Home Assistant Integration

Custom integration for Home Assistant that fetches operational data from `https://m.dk/api/operationsdata/`.

## Exposed entities

- **Sensor**: `M1/M2 message` with current message for lines M1/M2
- **Sensor**: `M3/M4 message` with current message for lines M3/M4
- **Sensor**: `Elevator outages` with per-station outage details in attributes

## Installation

### Option 1: HACS (recommended)

1. Open **HACS → Integrations → ⋮ (menu) → Custom repositories**.
2. Add this repository URL and set category to **Integration**.
3. Search for **Copenhagen Metro** in HACS and install it.
4. Restart Home Assistant.

### Option 2: Manual

1. Copy `custom_components/copenhagen_metro` to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

Add the integration through **Settings → Devices & Services → Add Integration → Copenhagen Metro**.

## Disclaimer

This project was 100% AI vibe coded. Please review code and behavior before production use.
