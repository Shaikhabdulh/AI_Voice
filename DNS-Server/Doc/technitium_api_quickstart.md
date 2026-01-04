# TECHNITIUM DNS SERVER API - QUICK START GUIDE
====================================================================================================

## 🚀 Getting Started

### Authentication Flow
```bash
# Step 1: Login to get a session token
curl -X POST "http://localhost:5380/api/user/login" \
  -d "user=admin&pass=admin"

# Response:
# {"token": "abc123...", "status": "ok"}

# Step 2: Use token in subsequent requests
TOKEN="your-token-here"
```

====================================================================================================


## 📌 User & Authentication
----------------------------------------------------------------------------------------------------

### Login
**Description:** Authenticate and get session token

**Request:**
```bash
curl -X POST "http://localhost:5380/api/user/login" \
  -d "user=admin&pass=admin&includeInfo=true"
```

**Response:**
```json
{
  "token": "932b2a3495852c15af01598f62563ae534460388",
  "username": "admin",
  "displayName": "Administrator",
  "status": "ok"
}
```


### Create API Token
**Description:** Create non-expiring API token for automation

**Request:**
```bash
curl -X POST "http://localhost:5380/api/user/createToken" \
  -d "user=admin&pass=admin&tokenName=MyAutomationToken"
```

**Response:**
```json
{
  "token": "permanent-token-abc123...",
  "tokenName": "MyAutomationToken",
  "status": "ok"
}
```


## 📌 Zone Management
----------------------------------------------------------------------------------------------------

### List All Zones
**Description:** Get all DNS zones

**Request:**
```bash
curl "http://localhost:5380/api/zones/list?token=$TOKEN"
```

**Response:**
```json
{
  "response": {
    "zones": [
      {"name": "example.com", "type": "Primary", "disabled": false},
      {"name": "test.com", "type": "Secondary", "disabled": false}
    ]
  },
  "status": "ok"
}
```


### Create Primary Zone
**Description:** Create a new primary DNS zone

**Request:**
```bash
curl -X POST "http://localhost:5380/api/zones/create" \
  -d "token=$TOKEN&zone=mydomain.com&type=Primary"
```

**Response:**
```json
{
  "response": {"domain": "mydomain.com"},
  "status": "ok"
}
```


### Add DNS A Record
**Description:** Add an A record to a zone

**Request:**
```bash
curl -X POST "http://localhost:5380/api/zones/records/add" \
  -d "token=$TOKEN&domain=mydomain.com&type=A&value=192.168.1.100&ttl=3600"
```

**Response:**
```json
{
  "status": "ok",
  "response": {"addedRecord": {...}}
}
```


## 📌 Dashboard & Statistics
----------------------------------------------------------------------------------------------------

### Get DNS Statistics
**Description:** Get query statistics for last hour

**Request:**
```bash
curl "http://localhost:5380/api/dashboard/stats/get?token=$TOKEN&type=LastHour"
```

**Response:**
```json
{
  "response": {
    "stats": {
      "totalQueries": 925,
      "totalNoError": 834,
      "totalBlocked": 49
    }
  },
  "status": "ok"
}
```


### Get Top Clients
**Description:** Get top DNS clients

**Request:**
```bash
curl "http://localhost:5380/api/dashboard/stats/getTop?token=$TOKEN&statsType=TopClients&limit=10"
```

**Response:**
```json
{
  "response": {
    "topClients": [
      {"name": "192.168.1.100", "hits": 463}
    ]
  },
  "status": "ok"
}
```


## 📌 Block Lists
----------------------------------------------------------------------------------------------------

### Block a Domain
**Description:** Add domain to blocklist

**Request:**
```bash
curl -X POST "http://localhost:5380/api/blocked/add" \
  -d "token=$TOKEN&domain=ads.example.com"
```

**Response:**
```json
{
  "status": "ok"
}
```


### Import Blocklist
**Description:** Import blocklist from URL

**Request:**
```bash
curl -X POST "http://localhost:5380/api/blocked/import" \
  -d "token=$TOKEN&listUrl=https://blocklist.site/list.txt"
```

**Response:**
```json
{
  "response": {"blockedZonesAdded": 1500},
  "status": "ok"
}
```


## 📌 DNS Client
----------------------------------------------------------------------------------------------------

### DNS Query
**Description:** Perform DNS resolution

**Request:**
```bash
curl "http://localhost:5380/api/dnsClient/resolve?token=$TOKEN&domain=example.com&type=A"
```

**Response:**
```json
{
  "response": {
    "result": {
      "Answer": [
        {"Name": "example.com", "Type": "A", "RDATA": "93.184.216.34"}
      ]
    }
  },
  "status": "ok"
}
```


## 📌 DHCP Server
----------------------------------------------------------------------------------------------------

### List DHCP Leases
**Description:** Get all DHCP leases

**Request:**
```bash
curl "http://localhost:5380/api/dhcp/leases/list?token=$TOKEN"
```

**Response:**
```json
{
  "response": {
    "leases": [
      {"address": "192.168.1.100", "hostname": "device1", "type": "Dynamic"}
    ]
  },
  "status": "ok"
}
```


## 📌 Server Settings
----------------------------------------------------------------------------------------------------

### Get DNS Settings
**Description:** Retrieve server configuration

**Request:**
```bash
curl "http://localhost:5380/api/settings/get?token=$TOKEN"
```

**Response:**
```json
{
  "response": {
    "dnsServerDomain": "dns.local",
    "recursion": "AllowOnlyForPrivateNetworks"
  },
  "status": "ok"
}
```


### Update Blocklists
**Description:** Force update all blocklists

**Request:**
```bash
curl -X POST "http://localhost:5380/api/settings/forceUpdateBlockLists?token=$TOKEN"
```

**Response:**
```json
{
  "status": "ok"
}
```


====================================================================================================

## 🔧 Common Patterns

### Error Handling
```json
{
  "status": "error",
  "errorMessage": "Invalid token or session expired",
  "stackTrace": "..."
}
```

### Pagination
```bash
curl "http://localhost:5380/api/zones/list?token=$TOKEN&pageNumber=1&zonesPerPage=10"
```

### Using Python
```python
import requests

# Login
response = requests.post('http://localhost:5380/api/user/login', data={
    'user': 'admin',
    'pass': 'admin'
})
token = response.json()['token']

# List zones
zones = requests.get('http://localhost:5380/api/zones/list', params={'token': token})
print(zones.json())

# Add DNS record
requests.post('http://localhost:5380/api/zones/records/add', data={
    'token': token,
    'domain': 'example.com',
    'type': 'A',
    'value': '192.168.1.100'
})

```

### Using JavaScript/Node.js
```javascript
const axios = require('axios');
const BASE_URL = 'http://localhost:5380';

// Login
const login = await axios.post(`${BASE_URL}/api/user/login`, 
    new URLSearchParams({ user: 'admin', pass: 'admin' })
);
const token = login.data.token;

// Get statistics
const stats = await axios.get(`${BASE_URL}/api/dashboard/stats/get`, {
    params: { token, type: 'LastHour' }
});
console.log(stats.data);

```