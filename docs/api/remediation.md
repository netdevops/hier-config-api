# Remediation Workflows

Generate and manage configuration remediation with tag-based filtering.

## Generate Remediation

Generate remediation and rollback configurations.

**Endpoint:** `POST /api/v1/remediation/generate`

### Request

```json
{
  "platform": "cisco_ios",
  "running_config": "hostname router1\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0",
  "intended_config": "hostname router2\ninterface GigabitEthernet0/0\n ip address 192.168.1.2 255.255.255.0",
  "tag_rules": [
    {
      "match_rules": ["hostname"],
      "tags": ["safe", "non-service-impacting"]
    }
  ],
  "include_tags": ["safe"],
  "exclude_tags": ["risky"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| platform | string | Yes | Platform type |
| running_config | string | Yes | Current configuration |
| intended_config | string | Yes | Desired configuration |
| tag_rules | array | No | Tag rules to apply |
| include_tags | array | No | Only include these tags |
| exclude_tags | array | No | Exclude these tags |

### Response

```json
{
  "remediation_id": "abc-123-def-456",
  "platform": "cisco_ios",
  "remediation_config": "no hostname router1\nhostname router2\ninterface GigabitEthernet0/0\n no ip address 192.168.1.1 255.255.255.0\n ip address 192.168.1.2 255.255.255.0",
  "rollback_config": "no hostname router2\nhostname router1\ninterface GigabitEthernet0/0\n no ip address 192.168.1.2 255.255.255.0\n ip address 192.168.1.1 255.255.255.0",
  "summary": {
    "additions": 4,
    "deletions": 4,
    "modifications": 0
  },
  "tags": {}
}
```

---

## Apply Tags

Apply tag rules to an existing remediation.

**Endpoint:** `POST /api/v1/remediation/{remediation_id}/tags`

### Request

```json
{
  "tag_rules": [
    {
      "match_rules": ["interface"],
      "tags": ["network-change", "review-required"]
    }
  ]
}
```

### Response

```json
{
  "remediation_id": "abc-123-def-456",
  "remediation_config": "...",
  "tags": {
    "0": ["network-change", "review-required"]
  }
}
```

---

## Filter Remediation

Filter remediation by tags.

**Endpoint:** `GET /api/v1/remediation/{remediation_id}/filter`

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| include_tags | array | Only include these tags |
| exclude_tags | array | Exclude these tags |

### Example

```bash
curl "http://localhost:8000/api/v1/remediation/abc-123/filter?include_tags=safe&exclude_tags=risky"
```

### Response

```json
{
  "remediation_id": "abc-123-def-456",
  "filtered_config": "hostname router2",
  "summary": {
    "additions": 1,
    "deletions": 0,
    "modifications": 0
  }
}
```
