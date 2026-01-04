# TECHNITIUM DNS SERVER API - COMPREHENSIVE SUMMARY
====================================================================================================

**Total API Endpoints:** 130
**Total Categories:** 13
**Document Generated:** 2026-01-04


## 📊 Category Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Administration | 32 | User/group management, permissions, clustering |
| Allow Lists | 6 | Manage allowed domains, whitelist operations |
| Block Lists | 6 | Manage blocked domains, import blocklists, ad-blocking |
| Cache Management | 3 | View/flush DNS cache, cache operations |
| DHCP Server | 12 | DHCP lease management, scope configuration |
| DNS Applications | 9 | Install/update DNS apps, app configuration |
| DNS Client | 1 | Perform DNS queries, resolution testing |
| Dashboard & Statistics | 3 | Query stats, top clients/domains, performance metrics |
| Logs & Monitoring | 5 | Query logs, log exports, monitoring |
| Other | 1 | Various operations |
| Server Settings | 7 | DNS server configuration, backups, forwarders |
| User & Authentication | 12 | Login, logout, 2FA, session management, API tokens |
| Zone Management | 33 | Create/manage DNS zones, DNSSEC, records (A, AAAA, CNAME, MX, etc.) |

====================================================================================================


## 📁 Administration
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Sessions | `/api/admin/sessions/list` | Administration: View | token, node (optional) |
| 2 | Create API Token | `/api/admin/sessions/createToken` | Administration: Modify | token, user, tokenName |
| 3 | Delete Session | `/api/admin/sessions/delete` | Administration: Delete | token, node (optional), partialToken |
| 4 | List Users | `/api/admin/users/list` | Administration: View | token, node (optional) |
| 5 | Create User | `/api/admin/users/create` | Administration: Modify | token, user, pass |
| 6 | Get User Details | `/api/admin/users/get` | Administration: View | token, node (optional), user |
| 7 | Set User Details | `/api/admin/users/set` | Administration: Modify | token, user, displayName (optional) |
| 8 | Delete User | `/api/admin/users/delete` | Administration: Delete | token, user |
| 9 | List Groups | `/api/admin/groups/list` | Administration: View | token, node (optional) |
| 10 | Create Group | `/api/admin/groups/create` | Administration: Modify | token, group, description (optional) |
| 11 | Get Group Details | `/api/admin/groups/get` | Administration: View | token, node (optional), group |
| 12 | Set Group Details | `/api/admin/groups/set` | Administration: Modify | token, group, newGroup (optional) |
| 13 | Delete Group | `/api/admin/groups/delete` | Administration: Delete | token, group |
| 14 | List Permissions | `/api/admin/permissions/list` | Administration: View | token, node (optional) |
| 15 | Get Permission Details | `/api/admin/permissions/get` | Administration: View | token, section, includeUsersAndGroups (optional) |
| 16 | Set Permission Details | `/api/admin/permissions/set` | Administration: Delete | token, node (optional), section |
| 17 | Get Cluster state | `/api/admin/cluster/state` | Administration: View | token, node (optional), includeServerIpAddresses (optional) |
| 18 | Initialize Cluster | `/api/admin/cluster/init` | Administration: Delete | token, clusterDomain, primaryNodeIpAddresses |
| 19 | Delete Cluster | `/api/admin/cluster/primary/delete` | Administration: Delete | token, node (optional), forceDelete (optional) |
| 20 | Join Cluster | `/api/admin/cluster/primary/join` | Administration: Delete | token, secondaryNodeId, secondaryNodeUrl |
| 21 | Remove Secondary Node | `/api/admin/cluster/primary/removeSecondary` | Administration: Delete | token, secondaryNodeId |
| 22 | Delete Secondary Node | `/api/admin/cluster/primary/deleteSecondary` | Administration: Delete | token, secondaryNodeId |
| 23 | Update Secondary Node | `/api/admin/cluster/primary/updateSecondary` | Administration: Delete | token, secondaryNodeId, secondaryNodeUrl |
| 24 | Transfer Config | `/api/admin/cluster/primary/transferConfig` | Administration: Delete | token, includeZones (optional), If-Modified-Since (optional) |
| 25 | Set Cluster Options | `/api/admin/cluster/primary/setOptions` | Administration: Modify | token, node (optional), heartbeatRefreshIntervalSeconds (optional) |
| 26 | Initialize And Join Cluster | `http://server2.home:5380/api/admin/cluster/initJoin` | Administration: Delete | token, secondaryNodeIpAddresses, primaryNodeUrl |
| 27 | Leave Cluster | `/api/admin/cluster/secondary/leave` | Administration: Delete | token, node (optional), forceLeave (optional) |
| 28 | Notify | `/api/admin/cluster/secondary/notify` | Administration: Delete | token, primaryNodeId, primaryNodeUrl |
| 29 | Resync Cluster | `/api/admin/cluster/secondary/resync` | Administration: Modify | token, node (optional) |
| 30 | Update Primary Node | `/api/admin/cluster/secondary/updatePrimary` | Administration: Modify | token, node (optional), primaryNodeUrl |
| 31 | Promote To Primary | `/api/admin/cluster/secondary/promote` | Administration: Delete | token, node (optional), forceDeletePrimary (optional) |
| 32 | Update Node IP Addresses | `/api/admin/cluster/updateIpAddresses` | Administration: Modify | token, node (optional), ipAddresses |


## 📁 Allow Lists
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Allowed Zones | `/api/allowed/list` | Allowed: View | token, node (optional), domain (Optional) |
| 2 | Allow Zone | `/api/allowed/add` | Allowed: Modify | token, domain |
| 3 | Delete Allowed Zone | `/api/allowed/delete` | Allowed: Delete | token, domain |
| 4 | Flush Allowed Zone | `/api/allowed/flush` | Allowed: Delete | token |
| 5 | Import Allowed Zones | `/api/allowed/import` | Allowed: Modify | token |
| 6 | Export Allowed Zones | `/api/allowed/export` | Allowed: View | token, node (optional) |


## 📁 Block Lists
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Blocked Zones | `/api/blocked/list` | Blocked: View | token, node (optional), domain (Optional) |
| 2 | Block Zone | `/api/blocked/add` | Blocked: Modify | token, domain |
| 3 | Delete Blocked Zone | `/api/blocked/delete` | Blocked: Delete | token, domain |
| 4 | Flush Blocked Zone | `/api/blocked/flush` | Blocked: Delete | token |
| 5 | Import Blocked Zones | `/api/blocked/import` | Blocked: Modify | token |
| 6 | Export Blocked Zones | `/api/blocked/export` | Blocked: View | token, node (optional) |


## 📁 Cache Management
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Cached Zones | `/api/cache/list` | Cache: View | token, domain (Optional), direction (Optional) |
| 2 | Delete Cached Zone | `/api/cache/delete` | Cache: Delete | token, domain |
| 3 | Flush DNS Cache | `/api/cache/flush` | Cache: Delete | token |


## 📁 DHCP Server
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List DHCP Leases | `/api/dhcp/leases/list` | DhcpServer: View | token |
| 2 | Remove DHCP Lease | `/api/dhcp/leases/remove` | DhcpServer: Delete | token, name, clientIdentifier (optional) |
| 3 | Convert To Reserved Lease | `/api/dhcp/leases/convertToReserved` | DhcpServer: Modify | token, name, clientIdentifier (optional) |
| 4 | Convert To Dynamic Lease | `/api/dhcp/leases/convertToDynamic` | DhcpServer: Modify | token, name, clientIdentifier (optional) |
| 5 | List DHCP Scopes | `/api/dhcp/scopes/list` | DhcpServer: View | token |
| 6 | Get DHCP Scope | `/api/dhcp/scopes/get` | DhcpServer: View | token, name |
| 7 | Set DHCP Scope | `/api/dhcp/scopes/set` | DhcpServer: Modify | token, name, newName (optional) |
| 8 | Add Reserved Lease | `/api/dhcp/scopes/addReservedLease` | DhcpServer: Modify | token, name, hardwareAddress |
| 9 | Remove Reserved Lease | `/api/dhcp/scopes/removeReservedLease` | DhcpServer: Modify | token, name, hardwareAddress |
| 10 | Enable DHCP Scope | `/api/dhcp/scopes/enable` | DhcpServer: Modify | token, name |
| 11 | Disable DHCP Scope | `/api/dhcp/scopes/disable` | DhcpServer: Modify | token, name |
| 12 | Delete DHCP Scope | `/api/dhcp/scopes/delete` | DhcpServer: Delete | token, name |


## 📁 DNS Applications
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Apps | `/api/apps/list` | Apps/Zones/Logs: View | token, node (optional) |
| 2 | List Store Apps | `/api/apps/listStoreApps` | Apps: View | token, node (optional) |
| 3 | Download And Install App | `/api/apps/downloadAndInstall` | Apps: Delete | token, name, url |
| 4 | Download And Update App | `/api/apps/downloadAndUpdate` | Apps: Delete | token, name, url |
| 5 | Install App | `/api/apps/install` | Apps: Delete | token, name |
| 6 | Update App | `/api/apps/update` | Apps: Delete | token, name |
| 7 | Uninstall App | `/api/apps/uninstall` | Apps: Delete | token, name |
| 8 | Get App Config | `/api/apps/config/get` | Apps: View | token, node (optional), name |
| 9 | Set App Config | `/api/apps/config/set` | Apps: Modify | token, name |


## 📁 DNS Client
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | Resolve Query | `/api/dnsClient/resolve` | DnsClient: View | token, node (optional), server |


## 📁 Dashboard & Statistics
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | Get Stats | `/api/dashboard/stats/get` | Dashboard: View | token, node, type (optional) |
| 2 | Get Top Stats | `/api/dashboard/stats/getTop` | Dashboard: View | token, node, type (optional) |
| 3 | Delete All Stats | `/api/dashboard/stats/deleteAll` | Dashboard: Delete | token, node |


## 📁 Logs & Monitoring
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Logs | `/api/logs/list` | Logs: View | token, node (optional) |
| 2 | Download Log | `/api/logs/download` | Logs: View | token, node (optional), fileName |
| 3 | Delete All Logs | `/api/logs/deleteAll` | Logs: Delete | token, node (optional) |
| 4 | Query Logs | `/api/logs/query` | Logs: View | token, node (optional), name |
| 5 | Export Query Logs | `/api/logs/export` | Logs: View | token, node (optional), name |


## 📁 Other
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | Delete Log | `` | Logs: Delete | token, node (optional), log |


## 📁 Server Settings
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | Get DNS Settings | `/api/settings/get` | Settings: View | token |
| 2 | Set DNS Settings | `/api/settings/set` | Settings: Modify | token, dnsServerDomain (optional), dnsServerLocalEndPoints (optional) |
| 3 | Get TSIG Key Names | `/api/settings/getTsigKeyNames` | Settings: View OR Zones: Modify | token |
| 4 | Force Update Block Lists | `/api/settings/forceUpdateBlockLists` | Settings: Modify | token |
| 5 | Temporarily Disable Block Lists | `/api/settings/temporaryDisableBlocking` | Settings: Modify | token, minutes |
| 6 | Backup Settings | `/api/settings/backup` | Settings: Delete | token, node (optional), authConfig (optional) |
| 7 | Restore Settings | `/api/settings/restore` | Settings: Delete | token, node (optional), authConfig (optional) |


## 📁 User & Authentication
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | Login | `/api/user/login` | None | user, pass, totp (optional) |
| 2 | Create API Token | `/api/user/createToken` | None | user, pass, totp (optional) |
| 3 | Logout | `/api/user/logout` | None | token |
| 4 | Get Session Info | `/api/user/session/get` | None | token |
| 5 | Delete User Session | `/api/user/session/delete` | None | token, partialToken |
| 6 | Change Password | `/api/user/changePassword` | None | token, pass, newPass |
| 7 | Initialize 2FA | `/api/user/2fa/init` | None | token |
| 8 | Enable 2FA | `/api/user/2fa/enable` | None | token, totp |
| 9 | Disable 2FA | `/api/user/2fa/disable` | None | token |
| 10 | Get User Profile Details | `/api/user/profile/get` | None | token |
| 11 | Set User Profile Details | `/api/user/profile/set` | None | token, displayName (optional), sessionTimeoutSeconds (optional) |
| 12 | Check For Update | `/api/user/checkForUpdate` | None | token |


## 📁 Zone Management
====================================================================================================

| # | API Name | Endpoint | Permissions | Key Parameters |
|---|----------|----------|-------------|----------------|
| 1 | List Zones | `/api/zones/list` | Zones: View\
Zone: View | token, node (optional), pageNumber (optional) |
| 2 | List Catalog Zones | `/api/zones/catalogs/list` | Zones: View\
Zone: View | token, node (optional) |
| 3 | Create Zone | `/api/zones/create` | Zones: Modify | token, node (optional), zone |
| 4 | Import Zone | `/api/zones/import` | Zones: Modify
Zone: Modify | token, node (optional), zone |
| 5 | Export Zone | `/api/zones/export` | Zones: View
Zone: View | token, node (optional), zone |
| 6 | Clone Zone | `/api/zones/clone` | Zones: Modify
Zone: View | token, node (optional), zone |
| 7 | Convert Zone Type | `/api/zones/convert` | Zones: Delete
Zone: Delete | token, node (optional), zone |
| 8 | Enable Zone | `/api/zones/enable` | Zones: Modify\
Zone: Modify | token, node (optional), zone |
| 9 | Disable Zone | `/api/zones/disable` | Zones: Modify\
Zone: Modify | token, node (optional), zone |
| 10 | Delete Zone | `/api/zones/delete` | Zones: Delete\
Zone: Delete | token, node (optional), zone |
| 11 | Resync Zone | `/api/zones/resync` | Zones: Modify\
Zone: Modify | token, node (optional), zone |
| 12 | Get Zone Options | `/api/zones/options/get` | Zones: Modify\
Zone: View | token, node (optional), zone |
| 13 | Set Zone Options | `/api/zones/options/set` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 14 | Get Zone Permissions | `/api/zones/permissions/get` | Zones: Modify\
Zone: View | token, node (optional), zone |
| 15 | Set Zone Permissions | `/api/zones/permissions/set` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 16 | Sign Zone | `/api/zones/dnssec/sign` |  | token, node (optional), zone |
| 17 | Unsign Zone | `/api/zones/dnssec/unsign` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 18 | Get DS Info | `/api/zones/dnssec/viewDS` | Zones: View\
Zone: View | token, node (optional), zone |
| 19 | Get DNSSEC Properties | `/api/zones/dnssec/properties/get` | Zones: Modify\
Zone: View | token, node (optional), zone |
| 20 | Convert To NSEC | `/api/zones/dnssec/properties/convertToNSEC` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 21 | Convert To NSEC3 | `/api/zones/dnssec/properties/convertToNSEC3` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 22 | Update NSEC3 Parameters | `/api/zones/dnssec/properties/updateNSEC3Params` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 23 | Update DNSKEY TTL | `/api/zones/dnssec/properties/updateDnsKeyTtl` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 24 | Add Private Key | `/api/zones/dnssec/properties/addPrivateKey` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 25 | Update Private Key | `/api/zones/dnssec/properties/updatePrivateKey` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 26 | Delete Private Key | `/api/zones/dnssec/properties/deletePrivateKey` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 27 | Publish All Private Keys | `/api/zones/dnssec/properties/publishAllPrivateKeys` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 28 | Rollover DNSKEY | `/api/zones/dnssec/properties/rolloverDnsKey` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 29 | Retire DNSKEY | `/api/zones/dnssec/properties/retireDnsKey` | Zones: Modify\
Zone: Delete | token, node (optional), zone |
| 30 | Add Record | `/api/zones/records/add` | Zones: None\
Zone: Modify | token, node (optional), domain |
| 31 | Get Records | `/api/zones/records/get` | Zones: None\
Zone: View | token, node (optional), domain |
| 32 | Update Record | `/api/zones/records/update` | Zones: None\
Zone: Modify | token, node (optional), domain |
| 33 | Delete Record | `/api/zones/records/delete` | Zones: None\
Zone: Delete | token, node (optional), domain |


====================================================================================================

## 🔍 Request & Response Patterns

### Common Request Patterns
```
GET  : Simple queries with query parameters
POST : Create/update operations with form data (application/x-www-form-urlencoded)
```

### Standard Response Structure
```json
{
  "status": "ok|error|invalid-token",
  "response": { ... },
  "errorMessage": "Error description (if error)",
  "stackTrace": "Stack trace (if error)"
}
```

### Authentication Methods
- **Session Token**: Short-lived token from `/api/user/login` (expires based on user settings)
- **API Token**: Long-lived token from `/api/user/createToken` (never expires)
- **Token Usage**: Include as `token` parameter in all authenticated requests

### HTTP Methods
- Most endpoints accept both **GET** and **POST**
- File uploads require **POST** with `Content-Type: multipart/form-data`
- Other requests use `Content-Type: application/x-www-form-urlencoded`