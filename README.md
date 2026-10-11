# Baseus Anti-Lost T2 — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![version](https://img.shields.io/github/v/release/jakubhegr18-design/homeassistant-baseus-anti-lost?include_prereleases)

A community Home Assistant integration for the **Baseus Anti-Lost T2** Bluetooth
tracker. It connects directly over Bluetooth Low Energy (BLE) and exposes
presence, signal strength, battery, distance estimate and anti-lost tracking
entities plus services and ready-made automations.

> [!WARNING]
> This is an **unofficial, community-made** integration. It is **not affiliated
> with, endorsed by, or supported by Baseus**. See the legal notice below.

## ⚠️ Legal notice

This project is provided for **educational and personal interoperability use only**.
By using it you acknowledge and agree that:

1. **Reverse engineering / fair use.** Behaviour and identifiers were determined
   by inspecting the publicly distributed Baseus Android application
   (v2.17.0.1) for interoperability purposes, which may fall under fair-use
   exceptions in your jurisdiction. No Baseus proprietary code or binaries are
   redistributed here.
2. **Account requirement.** The official Baseus mobile app requires an account
   to add and track devices. This integration offers **both** an account-based
   mode and a **Bluetooth-only** mode that performs all work locally without an
   account.
3. **Privacy & data.** In account mode some data may transit Baseus cloud
   servers. In Bluetooth-only mode no data leaves your Home Assistant host. Review
   the Baseus privacy policy before use.
4. **Compatibility.** Validated against the device signalling found in Baseus app
   v2.17.0.1. Firmware or app updates may break compatibility without notice.
5. **No warranty.** Provided "as is", without warranty of any kind. **Use at your
   own risk.**

## Installation

### HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jakubhegr18-design&repository=homeassistant-baseus-anti-lost&category=integration)

1. In Home Assistant go to **HACS → Integrations → ⋮ → Custom repositories**.
2. Add repository URL
   `https://github.com/jakubhegr18-design/homeassistant-baseus-anti-lost`
   with category **Integration**.
3. Search for **Baseus Anti-Lost T2**, download it and **restart Home Assistant**.

### Manual

Copy `custom_components/baseus_anti_lost` into your
`config/custom_components/` directory and restart Home Assistant.

## Configuration

The integration is set up entirely from the UI (**Settings → Devices & Services →
Add Integration → Baseus Anti-Lost T2**), which offers two modes:

- **Bluetooth (local, no account)** — picks a discovered Baseus tracker or asks
  for its Bluetooth (MAC) address.
- **Baseus account (cloud)** — signs in with your Baseus email/password and the
  tracker address.

### Options

| Option | Default | Description |
| --- | --- | --- |
| RSSI threshold (dBm) | `-80` | Signal level below which the tracker is treated as far away. |
| Out-of-range timeout (s) | `300` | Time without a sighting before the device is flagged out of range. |
| Notify when lost | `true` | Whether the lost events should trigger notifications. |
| Enable location tracking | `true` | Toggle location-related tracking. |

## Entities

**Sensors**

| Entity | Unit | Description |
| --- | --- | --- |
| `sensor…battery_level` | % | Battery charge |
| `sensor…signal_strength` | dBm | Latest RSSI |
| `sensor…connection_status` | – | `connected` / `disconnected` |
| `sensor…tracking_status` | – | `safe` / `out_of_range` / `lost` |
| `sensor…last_seen` | timestamp | Last time the device was heard |
| `sensor…distance_estimate` | m | Rough distance estimate from RSSI |

**Binary sensors**

| Entity | Device class | Description |
| --- | --- | --- |
| `binary_sensor…device_lost` | problem | On when the tracker is out of range |
| `binary_sensor…bluetooth_connected` | connectivity | On while connected |

**Switch**

| Entity | Description |
| --- | --- |
| `switch…anti_lost_enabled` | Enable/disable anti-lost tracking |

## Services

| Service | Description |
| --- | --- |
| `baseus_anti_lost.start_tracking` | Start anti-lost tracking |
| `baseus_anti_lost.stop_tracking` | Stop anti-lost tracking |
| `baseus_anti_lost.reset_device` | Reset the tracker state |

Each service accepts an optional `device_id` to target a specific tracker.

## Example automation

```yaml
automation:
  - alias: "Notify when the Anti-Lost T2 is lost"
    trigger:
      - platform: state
        entity_id: binary_sensor.anti_lost_t2_device_lost
        to: "on"
    action:
      - service: notify.mobile_app_phone
        data:
          title: "Tracker lost"
          message: "Your Baseus Anti-Lost T2 is out of range."
```

More ready-to-use examples live in [`examples/automation.yaml`](examples/automation.yaml).

## Troubleshooting

- Make sure Bluetooth is enabled on the Home Assistant host and the `bluetooth`
  integration is set up.
- The tracker must be awake/advertising to be discovered; press its button if
  needed.
- Account mode requires a valid Baseus account that already has the tracker
  paired in the official app.

## License

[MIT](LICENSE) © jakubhegr18-design. This project is not affiliated with Baseus.
