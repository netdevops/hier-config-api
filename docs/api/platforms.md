# Platform Information

Get platform-specific information and validate configurations.

## List Platforms

Get a list of all supported platforms.

**Endpoint:** `GET /api/v1/platforms`

### Response

```json
[
  {
    "platform_name": "cisco_ios",
    "display_name": "Cisco IOS",
    "vendor": "Cisco",
    "supported": true
  },
  {
    "platform_name": "cisco_nxos",
    "display_name": "Cisco NX-OS",
    "vendor": "Cisco",
    "supported": true
  },
  {
    "platform_name": "cisco_iosxr",
    "display_name": "Cisco IOS-XR",
    "vendor": "Cisco",
    "supported": true
  },
  {
    "platform_name": "juniper_junos",
    "display_name": "Juniper Junos",
    "vendor": "Juniper",
    "supported": true
  },
  {
    "platform_name": "arista_eos",
    "display_name": "Arista EOS",
    "vendor": "Arista",
    "supported": true
  }
]
```

---

## Get Platform Rules

Get platform-specific configuration rules.

**Endpoint:** `GET /api/v1/platforms/{platform}/rules`

### Example

```bash
curl http://localhost:8000/api/v1/platforms/cisco_ios/rules
```

### Response

```json
{
  "platform_name": "cisco_ios",
  "negation_default_when": [],
  "negation_negate_with": [],
  "ordering": [],
  "idempotent_commands_avoid": [],
  "idempotent_commands": []
}
```

| Field | Description |
|-------|-------------|
| negation_default_when | Default negation patterns |
| negation_negate_with | How to negate commands |
| ordering | Command ordering rules |
| idempotent_commands_avoid | Commands to avoid |
| idempotent_commands | Idempotent commands |

---

## Validate Configuration

Validate configuration for a specific platform.

**Endpoint:** `POST /api/v1/platforms/{platform}/validate`

### Request

```json
{
  "config_text": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"
}
```

### Response

```json
{
  "platform": "cisco_ios",
  "is_valid": true,
  "warnings": [
    "No NTP server configured"
  ],
  "errors": []
}
```

### Error Response

```json
{
  "platform": "cisco_ios",
  "is_valid": false,
  "warnings": [],
  "errors": [
    "Configuration parsing error: Invalid syntax on line 5"
  ]
}
```

## Supported Platforms

### Cisco IOS

**Platform ID:** `cisco_ios`

- Standard Cisco IOS devices
- Hierarchical configuration structure
- Full negation support

### Cisco NX-OS

**Platform ID:** `cisco_nxos`

- Cisco Nexus switches
- Data center switching platform
- Enhanced features support

### Cisco IOS-XR

**Platform ID:** `cisco_iosxr`

- Carrier-grade routers
- XML-based configuration
- Advanced routing features

### Juniper Junos

**Platform ID:** `juniper_junos`

- Juniper Networks devices
- Hierarchical configuration
- Commit-based changes

### Arista EOS

**Platform ID:** `arista_eos`

- Arista Networks switches
- Cloud networking platform
- Modern API support

### Generic

**Platform ID:** `generic`

- Fallback for unsupported platforms
- Basic hierarchical parsing
- Limited feature support
