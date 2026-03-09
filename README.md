# Copenhagen Metro Home Assistant Integration

Custom integration for Home Assistant that fetches live operational data and planned maintenance from [m.dk](https://m.dk).

## Entities

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.copenhagen_metro_m1_m2_message` | Current operational message for M1/M2 |
| `sensor.copenhagen_metro_m3_m4_message` | Current operational message for M3/M4 |
| `sensor.copenhagen_metro_elevator_outages` | Number of stations with elevator outages |
| `sensor.copenhagen_metro_m1_planned_maintenance` | Upcoming planned maintenance on M1 (next 7 days) |
| `sensor.copenhagen_metro_m2_planned_maintenance` | Upcoming planned maintenance on M2 (next 7 days) |
| `sensor.copenhagen_metro_m3_planned_maintenance` | Upcoming planned maintenance on M3 (next 7 days) |
| `sensor.copenhagen_metro_m4_planned_maintenance` | Upcoming planned maintenance on M4 (next 7 days) |

**Update intervals:** Live operational data refreshes every 5 minutes. Planned maintenance refreshes every hour.

---

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

---

## Dashboard Examples

### Live status overview

A simple card showing the current operational status for all lines.

```yaml
type: entities
title: Copenhagen Metro
entities:
  - entity: sensor.copenhagen_metro_m1_m2_message
    name: M1/M2
  - entity: sensor.copenhagen_metro_m3_m4_message
    name: M3/M4
  - entity: sensor.copenhagen_metro_elevator_outages
    name: Elevator outages
```

---

### Elevator outage at a specific station

Check whether the elevator at a particular station is currently out of service. Replace `Vanløse` with your station name as it appears in the integration's attributes.

**Conditional card** — only visible when the elevator is down:

```yaml
type: conditional
conditions:
  - condition: template
    value_template: >
      {{ state_attr('sensor.copenhagen_metro_elevator_outages', 'stations')
         | selectattr('station_name', 'equalto', 'Vanløse')
         | list | length > 0 }}
card:
  type: markdown
  content: >
    ## ⚠️ Elevator out of service — Vanløse
    {% set station = state_attr('sensor.copenhagen_metro_elevator_outages', 'stations')
       | selectattr('station_name', 'equalto', 'Vanløse') | first %}
    {% for msg in station.messages %}
    - {{ msg }}
    {% endfor %}
```

**Template sensor** — useful for automations and notifications:

```yaml
template:
  - sensor:
      - name: "Elevator Vanløse"
        state: >
          {{ state_attr('sensor.copenhagen_metro_elevator_outages', 'stations')
             | selectattr('station_name', 'equalto', 'Vanløse')
             | list | length > 0 }}
        attributes:
          messages: >
            {% set station = state_attr('sensor.copenhagen_metro_elevator_outages', 'stations')
               | selectattr('station_name', 'equalto', 'Vanløse') | first | default(none) %}
            {{ station.messages if station else [] }}
```

**All stations with active elevator outages** — markdown card listing every affected station:

```yaml
type: markdown
title: Elevator outages
content: >
  {% set stations = state_attr('sensor.copenhagen_metro_elevator_outages', 'stations') %}
  {% if stations | length == 0 %}
  ✅ All elevators are operational.
  {% else %}
  {% for station in stations %}
  ### {{ station.station_name }}
  {% for msg in station.messages %}
  - {{ msg }}
  {% endfor %}
  {% endfor %}
  {% endif %}
```

---

### Planned maintenance

**Upcoming maintenance on a specific line** — shows the next planned maintenance entry for M1:

```yaml
type: markdown
title: M1 planned maintenance
content: >
  {% set entries = state_attr('sensor.copenhagen_metro_m1_planned_maintenance', 'entries') %}
  {% if entries | length == 0 %}
  ✅ No planned maintenance in the next 7 days.
  {% else %}
  {% for entry in entries %}
  ### {{ entry.title }}
  🕐 {{ entry.start | as_datetime | as_local | strftime('%d %b %H:%M') }}
  → {{ entry.end | as_datetime | as_local | strftime('%H:%M') }}
  {% if entry.metro_bus %}🚌 Metro bus replacement{% endif %}

  {{ entry.description }}

  ---
  {% endfor %}
  {% endif %}
```

**Conditional alert — metro bus replacement coming up on M1 or M2:**

```yaml
type: conditional
conditions:
  - condition: template
    value_template: >
      {{ state_attr('sensor.copenhagen_metro_m1_planned_maintenance', 'entries')
         | selectattr('metro_bus', 'equalto', true) | list | length > 0
         or
         state_attr('sensor.copenhagen_metro_m2_planned_maintenance', 'entries')
         | selectattr('metro_bus', 'equalto', true) | list | length > 0 }}
card:
  type: markdown
  content: >
    ## 🚌 Metro bus replacement scheduled
    {% for line_sensor in [
         'sensor.copenhagen_metro_m1_planned_maintenance',
         'sensor.copenhagen_metro_m2_planned_maintenance'
       ] %}
    {% set entries = state_attr(line_sensor, 'entries')
       | selectattr('metro_bus', 'equalto', true) | list %}
    {% for entry in entries %}
    **{{ entry.title }}**
    {{ entry.start | as_datetime | as_local | strftime('%d %b %H:%M') }}
    → {{ entry.end | as_datetime | as_local | strftime('%H:%M') }}
    Affected lines: {{ entry.affected_lines | join(', ') }}

    {% endfor %}
    {% endfor %}
```

---

## Automation Examples

### Notify when elevator at your station is out of service

```yaml
automation:
  - alias: "Notify: Elevator outage at Kongens Nytorv"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.copenhagen_metro_elevator_outages', 'stations')
             | selectattr('station_name', 'equalto', 'Kongens Nytorv')
             | list | length > 0 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Elevator out of service"
          message: "The elevator at Kongens Nytorv is currently out of service."
```

### Notify when metro bus replacement is planned

```yaml
automation:
  - alias: "Notify: Metro bus replacement on M1"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.copenhagen_metro_m1_planned_maintenance', 'entries')
             | selectattr('metro_bus', 'equalto', true) | list | length > 0 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Metro bus replacement"
          message: >
            {% set entry = state_attr('sensor.copenhagen_metro_m1_planned_maintenance', 'entries')
               | selectattr('metro_bus', 'equalto', true) | first %}
            M1: {{ entry.title }} —
            {{ entry.start | as_datetime | as_local | strftime('%d %b %H:%M') }}
            to {{ entry.end | as_datetime | as_local | strftime('%H:%M') }}
```

---

## Disclaimer

This project was 100% AI vibe coded. Please review code and behavior before production use.
