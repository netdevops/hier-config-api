# Configuration Operations

Endpoints for parsing, comparing, and manipulating network configurations.

## Parse Configuration

Parse raw configuration text into a structured format.

**Endpoint:** `POST /api/v1/configs/parse`

### Request

```json
{
  "platform": "cisco_ios",
  "config_text": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| platform | string | Yes | Platform type (cisco_ios, cisco_nxos, etc.) |
| config_text | string | Yes | Raw configuration text |

### Response

```json
{
  "platform": "cisco_ios",
  "structured_config": {
    "text": "hostname router1",
    "children": [
      {
        "text": "interface GigabitEthernet0/0",
        "children": [
          {
            "text": "ip address 192.168.1.1 255.255.255.0",
            "children": []
          }
        ]
      }
    ]
  }
}
```

### Example

```bash
curl -X POST http://localhost:8000/api/v1/configs/parse \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "config_text": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"
  }'
```

---

## Compare Configurations

Compare running and intended configurations to identify differences.

**Endpoint:** `POST /api/v1/configs/compare`

### Request

```json
{
  "platform": "cisco_ios",
  "running_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0",
  "intended_config": "hostname router2\ninterface GigabitEthernet0/0\n ip address 192.168.1.2 255.255.255.0"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| platform | string | Yes | Platform type |
| running_config | string | Yes | Current configuration |
| intended_config | string | Yes | Desired configuration |

### Response

```json
{
  "platform": "cisco_ios",
  "unified_diff": "--- running_config\n+++ intended_config\n+ no hostname router1\n+ hostname router2\n- no hostname router2\n- hostname router1",
  "has_changes": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| platform | string | Platform type |
| unified_diff | string | Unified diff output |
| has_changes | boolean | Whether differences exist |

---

## Predict Configuration

Predict the future configuration state after applying commands.

**Endpoint:** `POST /api/v1/configs/predict`

### Request

```json
{
  "platform": "cisco_ios",
  "current_config": "hostname router1",
  "commands_to_apply": "interface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"
}
```

### Response

```json
{
  "platform": "cisco_ios",
  "predicted_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0"
}
```

---

## Merge Configurations

Merge multiple configuration snippets into a single configuration.

**Endpoint:** `POST /api/v1/configs/merge`

### Request

```json
{
  "platform": "cisco_ios",
  "configs": [
    "hostname router1",
    "interface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0",
    "interface GigabitEthernet0/1\n ip address 192.168.2.1 255.255.255.0"
  ]
}
```

### Response

```json
{
  "platform": "cisco_ios",
  "merged_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\ninterface GigabitEthernet0/1\n ip address 192.168.2.1 255.255.255.0"
}
```

---

## Search Configuration

Search configuration for lines matching specific patterns.

**Endpoint:** `POST /api/v1/configs/search`

### Request

```json
{
  "platform": "cisco_ios",
  "config_text": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\ninterface GigabitEthernet0/1\n ip address 192.168.2.1 255.255.255.0",
  "match_rules": {
    "contains": "interface"
  }
}
```

#### Match Rules

| Field | Type | Description |
|-------|------|-------------|
| equals | string | Exact match |
| contains | string | Substring match |
| startswith | string | Prefix match |
| regex | string | Regular expression |

### Response

```json
{
  "platform": "cisco_ios",
  "matches": [
    "interface GigabitEthernet0/0",
    "interface GigabitEthernet0/1"
  ],
  "match_count": 2
}
```

### Examples

**Search for interfaces:**

```bash
curl -X POST http://localhost:8000/api/v1/configs/search \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "config_text": "...",
    "match_rules": {
      "startswith": "interface"
    }
  }'
```

**Search using regex:**

```bash
curl -X POST http://localhost:8000/api/v1/configs/search \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "cisco_ios",
    "config_text": "...",
    "match_rules": {
      "regex": "ip address \\d+\\.\\d+\\.\\d+\\.\\d+"
    }
  }'
```
