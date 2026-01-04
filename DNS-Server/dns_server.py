from mcp.server.fastmcp import FastMCP
import requests
import os
import re
import ipaddress


# Initialize FastMCP server
mcp = FastMCP("dns-manager")


# Configuration
DNS_URL = os.getenv("DNS_SERVER_URL", "http://localhost:5380")
API_TOKEN = os.getenv("DNS_API_TOKEN", "6ee8a572a97dc8dd2827d3f9fa55e17eb651969ed1149aba47666bc449670077")


def validate_domain(domain: str) -> bool:
    """Validate domain name format"""
    if not domain or len(domain) > 253:
        return False
    
    # Remove trailing dot if present
    domain = domain.rstrip('.')
    
    # Check each label
    labels = domain.split('.')
    if len(labels) < 2:
        return False
    
    domain_regex = re.compile(
        r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$'
    )
    
    return all(domain_regex.match(label) for label in labels)


def validate_ip(ip: str) -> bool:
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_record_name(name: str) -> bool:
    """Validate DNS record name"""
    if not name or len(name) > 63:
        return False
    
    # Allow @ for apex records
    if name == "@":
        return True
    
    # DNS label regex (RFC 1123)
    name_regex = re.compile(
        r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$'
    )
    
    return bool(name_regex.match(name))


@mcp.tool()
def add_dns_record(
    domain: str, 
    name: str, 
    ip: str, 
    ttl: int = 3600
) -> dict:
    """
    Add a DNS A record to Technitium DNS server with validation.
    
    Args:
        domain: Base domain name (e.g., "example.com")
        name: Record name - use "@" for apex, or subdomain like "www", "api" (e.g., "www")
        ip: IPv4 address (e.g., "192.168.1.100")
        ttl: Time to live in seconds, 3600 default (e.g., 3600)
    """
    
    # Validate inputs
    errors = []
    
    if not validate_domain(domain):
        errors.append(f"Invalid domain format: '{domain}'")
    
    if not validate_record_name(name):
        errors.append(f"Invalid record name format: '{name}'")
    
    if not validate_ip(ip):
        errors.append(f"Invalid IP address format: '{ip}'")
    
    if not isinstance(ttl, int) or ttl < 1 or ttl > 86400:
        errors.append(f"TTL must be integer between 1-86400 seconds")
    
    if errors:
        return {
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    
    # Sanitize inputs
    domain = domain.strip().lower()
    name = name.strip().lower()
    ip = ip.strip()
    
    # Build full domain name
    full_domain = f"{name}.{domain}" if name != "@" else domain
    
    # Make API request
    try:
        response = requests.post(
            f"{DNS_URL}/api/zones/records/add",
            data={
                "token": API_TOKEN,
                "domain": full_domain,
                "type": "A",
                "ipAddress": ip,
                "ttl": ttl
            },
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            return {
                "success": True,
                "message": f"Record added: {full_domain} -> {ip}",
                "details": {
                    "domain": full_domain,
                    "ip": ip,
                    "ttl": ttl
                }
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def get_dns_records(
    domain: str,
    zone: str = None,
    list_zone: bool = False
) -> dict:
    """
    Get DNS records for a domain from Technitium DNS server.
    
    Args:
        domain: The domain name to get records for (e.g., "example.com" or "api.example.com")
        zone: Optional zone name. If not specified, closest authoritative zone is used (e.g., "example.com")
        list_zone: If True, lists all records in the zone. If False, lists only records for the given domain (default: False)
    """
    
    # Validate domain
    if not validate_domain(domain):
        return {
            "success": False,
            "error": "Validation failed",
            "details": [f"Invalid domain format: '{domain}'"]
        }
    
    # Validate zone if provided
    if zone and not validate_domain(zone):
        return {
            "success": False,
            "error": "Validation failed",
            "details": [f"Invalid zone format: '{zone}'"]
        }
    
    # Sanitize inputs
    domain = domain.strip().lower()
    if zone:
        zone = zone.strip().lower()
    
    # Build request parameters
    params = {
        "token": API_TOKEN,
        "domain": domain,
        "listZone": "true" if list_zone else "false"
    }
    
    if zone:
        params["zone"] = zone
    
    # Make API request
    try:
        response = requests.get(
            f"{DNS_URL}/api/zones/records/get",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            zone_info = result.get("response", {}).get("zone", {})
            records = result.get("response", {}).get("records", [])
            
            # Simplify records - filter out DNSSEC records for cleaner output
            simplified_records = []
            for record in records:
                # Skip DNSSEC-related records for cleaner output
                if record.get("type") in ["RRSIG", "DNSKEY", "NSEC3", "NSEC3PARAM", "DS"]:
                    continue
                
                simplified_record = {
                    "name": record.get("name"),
                    "type": record.get("type"),
                    "ttl": record.get("ttl"),
                    "disabled": record.get("disabled", False)
                }
                
                # Add type-specific data
                rdata = record.get("rData", {})
                if record.get("type") == "A":
                    simplified_record["ip"] = rdata.get("ipAddress")
                elif record.get("type") == "AAAA":
                    simplified_record["ip"] = rdata.get("ipAddress")
                elif record.get("type") == "CNAME":
                    simplified_record["cname"] = rdata.get("cname")
                elif record.get("type") == "MX":
                    simplified_record["exchange"] = rdata.get("exchange")
                    simplified_record["preference"] = rdata.get("preference")
                elif record.get("type") == "TXT":
                    simplified_record["text"] = rdata.get("text")
                elif record.get("type") == "NS":
                    simplified_record["nameServer"] = rdata.get("nameServer")
                elif record.get("type") == "SOA":
                    simplified_record["primaryNameServer"] = rdata.get("primaryNameServer")
                    simplified_record["responsiblePerson"] = rdata.get("responsiblePerson")
                    simplified_record["serial"] = rdata.get("serial")
                else:
                    simplified_record["data"] = rdata
                
                simplified_records.append(simplified_record)
            
            return {
                "success": True,
                "zone": {
                    "name": zone_info.get("name"),
                    "type": zone_info.get("type"),
                    "disabled": zone_info.get("disabled", False)
                },
                "record_count": len(simplified_records),
                "records": simplified_records
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def find_domain_by_ip(
    ip: str,
    zone: str = ""
) -> dict:
    """
    Find which domain names point to a specific IP address (reverse lookup).
    
    Args:
        ip: The IP address to search for (e.g., "192.168.1.100")
        zone: Optional zone name to search within. If not specified, searches all zones (e.g., "example.com")
    """
    
    # Validate IP
    if not validate_ip(ip):
        return {
            "success": False,
            "error": "Validation failed",
            "details": [f"Invalid IP address format: '{ip}'"]
        }
    
    # Validate zone if provided
    if zone and not validate_domain(zone):
        return {
            "success": False,
            "error": "Validation failed",
            "details": [f"Invalid zone format: '{zone}'"]
        }
    
    ip = ip.strip()
    
    # If zone is specified, search within that zone
    if zone:
        zone = zone.strip().lower()
        params = {
            "token": API_TOKEN,
            "domain": zone,
            "listZone": "true"
        }
        
        try:
            response = requests.get(
                f"{DNS_URL}/api/zones/records/get",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "ok":
                records = result.get("response", {}).get("records", [])
                matching_domains = []
                
                # Search for matching IP
                for record in records:
                    if record.get("type") in ["A", "AAAA"]:
                        rdata = record.get("rData", {})
                        if rdata.get("ipAddress") == ip:
                            matching_domains.append({
                                "name": record.get("name"),
                                "type": record.get("type"),
                                "ttl": record.get("ttl"),
                                "ip": ip,
                                "disabled": record.get("disabled", False)
                            })
                
                if matching_domains:
                    return {
                        "success": True,
                        "ip": ip,
                        "zone": zone,
                        "found_count": len(matching_domains),
                        "domains": matching_domains
                    }
                else:
                    return {
                        "success": True,
                        "ip": ip,
                        "zone": zone,
                        "found_count": 0,
                        "domains": [],
                        "message": f"No domains found pointing to {ip} in zone {zone}"
                    }
            else:
                return {
                    "success": False,
                    "error": "DNS server error",
                    "details": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }
    
    else:
        # Search across all zones
        try:
            # First, get list of all zones
            list_response = requests.get(
                f"{DNS_URL}/api/zones/list",
                params={"token": API_TOKEN},
                timeout=10
            )
            list_response.raise_for_status()
            list_result = list_response.json()
            
            if list_result.get("status") != "ok":
                return {
                    "success": False,
                    "error": "Failed to list zones",
                    "details": list_result.get("error", "Unknown error")
                }
            
            zones = list_result.get("response", {}).get("zones", [])
            all_matching_domains = []
            
            # Search each zone
            for zone_info in zones:
                zone_name = zone_info.get("name")
                if not zone_name:
                    continue
                
                # Get records for this zone
                params = {
                    "token": API_TOKEN,
                    "domain": zone_name,
                    "listZone": "true"
                }
                
                try:
                    response = requests.get(
                        f"{DNS_URL}/api/zones/records/get",
                        params=params,
                        timeout=10
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    if result.get("status") == "ok":
                        records = result.get("response", {}).get("records", [])
                        
                        for record in records:
                            if record.get("type") in ["A", "AAAA"]:
                                rdata = record.get("rData", {})
                                if rdata.get("ipAddress") == ip:
                                    all_matching_domains.append({
                                        "name": record.get("name"),
                                        "zone": zone_name,
                                        "type": record.get("type"),
                                        "ttl": record.get("ttl"),
                                        "ip": ip,
                                        "disabled": record.get("disabled", False)
                                    })
                except:
                    continue  # Skip zones that fail
            
            if all_matching_domains:
                return {
                    "success": True,
                    "ip": ip,
                    "found_count": len(all_matching_domains),
                    "domains": all_matching_domains
                }
            else:
                return {
                    "success": True,
                    "ip": ip,
                    "found_count": 0,
                    "domains": [],
                    "message": f"No domains found pointing to {ip} across all zones"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }

@mcp.tool()
def update_dns_record(
    domain: str,
    current_ip: str,
    new_ip: str,
    zone: str = "",
    ttl: int = None,
    disable: bool = False
) -> dict:
    """
    Update an existing DNS A record's IP address in Technitium DNS server.
    Use this when user wants to change the IP ADDRESS, not the domain name.
    
    Examples of when to use this tool:
    - "change api.example.com IP from 1.1.1.1 to 2.2.2.2"
    - "update example.com to point to 3.3.3.3 instead of 4.4.4.4"
    - "modify IP address of test.com from old IP to new IP"
    
    Args:
        domain: The domain name (e.g., "api.example.com")
        current_ip: The CURRENT IP address - must be numbers (e.g., "192.168.1.100")
        new_ip: The NEW IP address - must be numbers (e.g., "192.168.1.200")
        zone: Optional zone name (e.g., "example.com")
        ttl: Optional new TTL in seconds (e.g., 7200)
        disable: Set to True to disable the record (default: False)
    """
    
    # Validate inputs
    errors = []
    
    if not validate_domain(domain):
        errors.append(f"Invalid domain format: '{domain}'")
    
    if zone and not validate_domain(zone):
        errors.append(f"Invalid zone format: '{zone}'")
    
    if not validate_ip(current_ip):
        errors.append(f"Invalid current IP address format: '{current_ip}'")
    
    if not validate_ip(new_ip):
        errors.append(f"Invalid new IP address format: '{new_ip}'")
    
    if ttl is not None and (not isinstance(ttl, int) or ttl < 1 or ttl > 86400):
        errors.append(f"TTL must be integer between 1-86400 seconds")
    
    if errors:
        return {
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    
    # Sanitize inputs
    domain = domain.strip().lower()
    current_ip = current_ip.strip()
    new_ip = new_ip.strip()
    if zone:
        zone = zone.strip().lower()
    
    # Build request parameters
    params = {
        "token": API_TOKEN,
        "domain": domain,
        "type": "A",
        "ipAddress": current_ip,
        "newIpAddress": new_ip,
        "disable": "true" if disable else "false"
    }
    
    if zone:
        params["zone"] = zone
    
    if ttl is not None:
        params["ttl"] = ttl
    
    # Make API request
    try:
        response = requests.post(
            f"{DNS_URL}/api/zones/records/update",
            data=params,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            updated_record = result.get("response", {}).get("updatedRecord", {})
            
            return {
                "success": True,
                "message": f"Record updated: {domain} changed from {current_ip} to {new_ip}",
                "details": {
                    "domain": domain,
                    "old_ip": current_ip,
                    "new_ip": new_ip,
                    "ttl": updated_record.get("ttl"),
                    "disabled": updated_record.get("disabled", False)
                }
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def rename_dns_record(
    old_domain: str,
    new_domain: str,
    record_type: str = "A",
    zone: str = ""
) -> dict:
    """
    Rename a DNS record (change its domain name) in Technitium DNS server.
    
    Args:
        old_domain: The current domain name (e.g., "sara.data.com")
        new_domain: The new domain name (e.g., "tara.data.com")
        record_type: The record type to rename (default: "A")
        zone: Optional zone name. If not specified, closest authoritative zone is used (e.g., "data.com")
    """
    
    # Validate inputs
    errors = []
    
    if not validate_domain(old_domain):
        errors.append(f"Invalid old domain format: '{old_domain}'")
    
    if not validate_domain(new_domain):
        errors.append(f"Invalid new domain format: '{new_domain}'")
    
    if zone and not validate_domain(zone):
        errors.append(f"Invalid zone format: '{zone}'")
    
    if errors:
        return {
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    
    # Sanitize inputs
    old_domain = old_domain.strip().lower()
    new_domain = new_domain.strip().lower()
    record_type = record_type.strip().upper()
    if zone:
        zone = zone.strip().lower()
    
    # First, get the existing record to know its current values
    get_params = {
        "token": API_TOKEN,
        "domain": old_domain,
        "listZone": "false"
    }
    if zone:
        get_params["zone"] = zone
    
    try:
        # Get existing record
        get_response = requests.get(
            f"{DNS_URL}/api/zones/records/get",
            params=get_params,
            timeout=10
        )
        get_response.raise_for_status()
        get_result = get_response.json()
        
        if get_result.get("status") != "ok":
            return {
                "success": False,
                "error": "Failed to get existing record",
                "details": get_result.get("error", "Unknown error")
            }
        
        # Find the record we want to rename
        records = get_result.get("response", {}).get("records", [])
        target_record = None
        
        for record in records:
            if record.get("name") == old_domain and record.get("type") == record_type:
                target_record = record
                break
        
        if not target_record:
            return {
                "success": False,
                "error": "Record not found",
                "details": f"No {record_type} record found for {old_domain}"
            }
        
        # Build update request based on record type
        update_params = {
            "token": API_TOKEN,
            "domain": old_domain,
            "type": record_type,
            "newDomain": new_domain,
            "ttl": target_record.get("ttl", 3600)
        }
        
        if zone:
            update_params["zone"] = zone
        
        # Add type-specific parameters
        rdata = target_record.get("rData", {})
        
        if record_type == "A":
            ip_address = rdata.get("ipAddress")
            if not ip_address:
                return {
                    "success": False,
                    "error": "Missing IP address",
                    "details": "Could not find IP address in existing record"
                }
            update_params["ipAddress"] = ip_address
        elif record_type == "CNAME":
            cname = rdata.get("cname")
            if not cname:
                return {
                    "success": False,
                    "error": "Missing CNAME",
                    "details": "Could not find CNAME in existing record"
                }
            update_params["cname"] = cname
        else:
            return {
                "success": False,
                "error": "Unsupported record type",
                "details": f"Renaming {record_type} records is not yet supported. Only A and CNAME records can be renamed."
            }
        
        # Make API request to rename
        response = requests.post(
            f"{DNS_URL}/api/zones/records/update",
            data=update_params,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            return {
                "success": True,
                "message": f"Record renamed: {old_domain} → {new_domain}",
                "details": {
                    "old_domain": old_domain,
                    "new_domain": new_domain,
                    "type": record_type,
                    "ttl": update_params["ttl"]
                }
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def delete_dns_record(
    domain: str,
    record_type: str = "A",
    ip: str = "",
    value: str = "",
    zone: str = ""
) -> dict:
    """
    Delete a DNS record from Technitium DNS server.
    
    Args:
        domain: The domain name of the record to delete (e.g., "api.example.com")
        record_type: The type of record to delete (default: "A"). Supported: A, AAAA, CNAME, TXT, MX, NS
        ip: Required for A/AAAA records - the IP address to delete (e.g., "192.168.1.100")
        value: Required for other record types - the value to delete (e.g., CNAME target, TXT content)
        zone: Optional zone name. If not specified, closest authoritative zone is used (e.g., "example.com")
    """
    
    # Validate inputs
    errors = []
    
    if not validate_domain(domain):
        errors.append(f"Invalid domain format: '{domain}'")
    
    if zone and not validate_domain(zone):
        errors.append(f"Invalid zone format: '{zone}'")
    
    record_type = record_type.strip().upper()
    
    # Validate based on record type
    if record_type in ["A", "AAAA"]:
        if not ip:
            errors.append(f"IP address is required for {record_type} record deletion")
        elif not validate_ip(ip):
            errors.append(f"Invalid IP address format: '{ip}'")
    elif record_type in ["CNAME", "TXT", "NS"]:
        if not value:
            errors.append(f"Value is required for {record_type} record deletion")
    
    if errors:
        return {
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    
    # Sanitize inputs
    domain = domain.strip().lower()
    ip = ip.strip() if ip else ""
    value = value.strip() if value else ""
    if zone:
        zone = zone.strip().lower()
    
    # Build request parameters
    params = {
        "token": API_TOKEN,
        "domain": domain,
        "type": record_type
    }
    
    if zone:
        params["zone"] = zone
    
    # Add type-specific parameters
    if record_type in ["A", "AAAA"]:
        params["ipAddress"] = ip
    elif record_type == "CNAME":
        params["cname"] = value
    elif record_type == "TXT":
        params["text"] = value
    elif record_type == "NS":
        params["nameServer"] = value
    elif record_type == "MX":
        # For MX, we might need both preference and exchange
        # If value contains a comma, split it
        if ',' in value:
            preference, exchange = value.split(',', 1)
            params["preference"] = preference.strip()
            params["exchange"] = exchange.strip()
        else:
            params["exchange"] = value
            params["preference"] = "10"  # Default
    
    # Make API request to delete
    try:
        response = requests.post(
            f"{DNS_URL}/api/zones/records/delete",
            data=params,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            message = f"Record deleted: {domain}"
            if record_type in ["A", "AAAA"]:
                message += f" ({record_type}: {ip})"
            elif value:
                message += f" ({record_type}: {value})"
            else:
                message += f" ({record_type})"
            
            return {
                "success": True,
                "message": message,
                "details": {
                    "domain": domain,
                    "type": record_type,
                    "zone": zone if zone else "auto-detected"
                }
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def create_dns_zone(
    zone: str,
    zone_type: str = "Primary",
    use_soa_serial_date_scheme: bool = False
) -> dict:
    """
    Create a new DNS zone in Technitium DNS server.
    
    Args:
        zone: The domain name for the new zone (e.g., "example.com", "test.local")
        zone_type: The type of zone to create (default: "Primary"). Valid values: Primary, Secondary, Stub, Forwarder
        use_soa_serial_date_scheme: Use date scheme for SOA serial (default: False)
    """
    
    # Validate inputs
    errors = []
    
    if not validate_domain(zone):
        errors.append(f"Invalid zone format: '{zone}'")
    
    zone_type = zone_type.strip().title()  # Capitalize properly
    valid_types = ["Primary", "Secondary", "Stub", "Forwarder", "SecondaryForwarder", "Catalog", "SecondaryCatalog"]
    if zone_type not in valid_types:
        errors.append(f"Invalid zone type: '{zone_type}'. Valid types: {', '.join(valid_types)}")
    
    if errors:
        return {
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    
    # Sanitize inputs
    zone = zone.strip().lower()
    
    # Check if zone already exists
    try:
        list_response = requests.get(
            f"{DNS_URL}/api/zones/list",
            params={"token": API_TOKEN},
            timeout=10
        )
        list_response.raise_for_status()
        list_result = list_response.json()
        
        if list_result.get("status") == "ok":
            zones = list_result.get("response", {}).get("zones", [])
            
            for z in zones:
                if z.get("name") == zone:
                    return {
                        "success": False,
                        "error": "Zone already exists",
                        "details": f"Zone '{zone}' already exists as {z.get('type')} zone"
                    }
    except Exception as e:
        return {
            "success": False,
            "error": "Failed to check existing zones",
            "details": str(e)
        }
    
    # Build request parameters
    params = {
        "token": API_TOKEN,
        "zone": zone,
        "type": zone_type
    }
    
    if use_soa_serial_date_scheme:
        params["useSoaSerialDateScheme"] = "true"
    
    # Make API request to create zone
    try:
        response = requests.post(
            f"{DNS_URL}/api/zones/create",
            data=params,
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            created_domain = result.get("response", {}).get("domain", zone)
            
            return {
                "success": True,
                "message": f"Zone created: {created_domain}",
                "details": {
                    "zone": created_domain,
                    "type": zone_type,
                    "soa_serial_date_scheme": use_soa_serial_date_scheme
                }
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def list_dns_zones() -> dict:
    """
    List all DNS zones in Technitium DNS server.
    
    Shows all zones with their type, status, and record count.
    """
    
    try:
        response = requests.get(
            f"{DNS_URL}/api/zones/list",
            params={"token": API_TOKEN},
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            zones = result.get("response", {}).get("zones", [])
            
            # Simplify zone information
            simplified_zones = []
            for zone in zones:
                simplified_zones.append({
                    "name": zone.get("name"),
                    "type": zone.get("type"),
                    "disabled": zone.get("disabled", False),
                    "internal": zone.get("internal", False),
                    "dnssec_status": zone.get("dnssecStatus", "Unknown")
                })
            
            return {
                "success": True,
                "zone_count": len(simplified_zones),
                "zones": simplified_zones
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }


@mcp.tool()
def delete_dns_zone(
    zone: str,
    confirm: bool = False
) -> dict:
    """
    Delete an entire DNS zone from Technitium DNS server.
    
    ⚠️ WARNING: This deletes ALL records in the zone! This action cannot be undone.
    
    Args:
        zone: The zone name to delete (e.g., "example.com", "test.local")
        confirm: Must be set to True to confirm deletion. This is a safety measure.
    """
    
    # Validate inputs
    errors = []
    
    if not validate_domain(zone):
        errors.append(f"Invalid zone format: '{zone}'")
    
    if not confirm:
        errors.append("Deletion not confirmed. Set confirm=True to proceed with zone deletion.")
    
    if errors:
        return {
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    
    # Sanitize inputs
    zone = zone.strip().lower()
    
    # First, check if zone exists and get info
    try:
        list_response = requests.get(
            f"{DNS_URL}/api/zones/list",
            params={"token": API_TOKEN},
            timeout=10
        )
        list_response.raise_for_status()
        list_result = list_response.json()
        
        if list_result.get("status") == "ok":
            zones = list_result.get("response", {}).get("zones", [])
            zone_exists = False
            zone_info = None
            
            for z in zones:
                if z.get("name") == zone:
                    zone_exists = True
                    zone_info = z
                    break
            
            if not zone_exists:
                return {
                    "success": False,
                    "error": "Zone not found",
                    "details": f"Zone '{zone}' does not exist"
                }
    except Exception as e:
        return {
            "success": False,
            "error": "Failed to verify zone",
            "details": str(e)
        }
    
    # Make API request to delete zone
    try:
        response = requests.post(
            f"{DNS_URL}/api/zones/delete",
            data={
                "token": API_TOKEN,
                "zone": zone
            },
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("status") == "ok":
            return {
                "success": True,
                "message": f"Zone deleted: {zone}",
                "details": {
                    "zone": zone,
                    "type": zone_info.get("type") if zone_info else "unknown",
                    "warning": "All records in this zone have been permanently deleted"
                }
            }
        else:
            return {
                "success": False,
                "error": "DNS server error",
                "details": result.get("error", "Unknown error")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "details": "DNS server did not respond within 10 seconds"
        }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "details": f"Cannot connect to DNS server at {DNS_URL}"
        }
            
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": "HTTP error",
            "details": f"Server returned {e.response.status_code}"
        }
            
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
            "details": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
