"""
URL validation to prevent SSRF attacks.

Session 185: Security fix - Validate URLs before downloading to prevent
Server-Side Request Forgery (SSRF) attacks that could access internal resources.
"""

import ipaddress
import socket
import logging
from urllib.parse import urlparse
from typing import Tuple, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# Allowed domains for video/media downloads
# Add trusted CDN domains here
DEFAULT_ALLOWED_DOMAINS = [
    'cdn.runwayml.com',
    'storage.googleapis.com',
    'res.cloudinary.com',
    's3.amazonaws.com',
    's3.us-east-1.amazonaws.com',
    's3.us-west-2.amazonaws.com',
    'replicate.delivery',
    'api.replicate.com',
    'pub-3626123a908346a7a8be8d9295f44e26.r2.dev',  # Replicate R2 storage
    'elevenlabs.io',
    'api.elevenlabs.io',
    'storage.elevenlabs.io',
    'api.stability.ai',
]

# Private IP ranges to block (SSRF protection)
PRIVATE_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local
    ipaddress.ip_network('0.0.0.0/8'),  # Current network
    ipaddress.ip_network('100.64.0.0/10'),  # Carrier-grade NAT
    ipaddress.ip_network('198.18.0.0/15'),  # Network benchmark testing
    ipaddress.ip_network('224.0.0.0/4'),  # Multicast
    ipaddress.ip_network('240.0.0.0/4'),  # Reserved
    ipaddress.ip_network('255.255.255.255/32'),  # Broadcast
    # IPv6 private ranges
    ipaddress.ip_network('::1/128'),  # IPv6 localhost
    ipaddress.ip_network('fc00::/7'),  # IPv6 unique local
    ipaddress.ip_network('fe80::/10'),  # IPv6 link local
]


def get_allowed_domains() -> List[str]:
    """
    Get the list of allowed domains for URL downloads.

    Can be configured via settings.ALLOWED_VIDEO_DOMAINS or defaults to
    the built-in list of trusted CDN providers.
    """
    return getattr(settings, 'ALLOWED_VIDEO_DOMAINS', DEFAULT_ALLOWED_DOMAINS)


def is_private_ip(ip_str: str) -> bool:
    """
    Check if an IP address is in a private/reserved range.

    Args:
        ip_str: IP address string

    Returns:
        True if IP is private/reserved, False if public
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in PRIVATE_RANGES)
    except ValueError:
        # Invalid IP format - treat as private for safety
        return True


def is_domain_allowed(hostname: str, allowed_domains: Optional[List[str]] = None) -> bool:
    """
    Check if a hostname is in the allowed domains list.

    Supports exact matches and wildcard subdomains (domains starting with .).

    Args:
        hostname: The hostname to check
        allowed_domains: List of allowed domains (or None to use defaults)

    Returns:
        True if domain is allowed, False otherwise
    """
    if allowed_domains is None:
        allowed_domains = get_allowed_domains()

    hostname_lower = hostname.lower()

    for domain in allowed_domains:
        domain_lower = domain.lower()
        if domain_lower.startswith('.'):
            # Wildcard domain - allow subdomains
            if hostname_lower.endswith(domain_lower) or hostname_lower == domain_lower[1:]:
                return True
        else:
            # Exact match
            if hostname_lower == domain_lower:
                return True

    return False


def validate_url(
    url: str,
    check_domain: bool = True,
    check_ip: bool = True,
    allowed_domains: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """
    Validate a URL for safe downloading.

    Checks:
    1. URL uses http or https scheme
    2. URL has a valid hostname
    3. Hostname is in the allowed domains list (if check_domain=True)
    4. Resolved IP is not in private ranges (if check_ip=True)

    Args:
        url: The URL to validate
        check_domain: Whether to check against domain allowlist
        check_ip: Whether to check resolved IP against private ranges
        allowed_domains: Custom list of allowed domains (optional)

    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, error_message will be empty string
    """
    try:
        # Parse URL
        parsed = urlparse(url)

        # Must be http or https
        if parsed.scheme not in ('http', 'https'):
            return False, f"URL scheme must be http or https, got: {parsed.scheme}"

        # Must have a hostname
        if not parsed.hostname:
            return False, "URL must have a valid hostname"

        hostname = parsed.hostname.lower()

        # Check domain allowlist
        if check_domain:
            if not is_domain_allowed(hostname, allowed_domains):
                logger.warning(f"SSRF Protection: Domain not allowed: {hostname}")
                return False, f"Domain not allowed: {hostname}"

        # Check for private IPs
        if check_ip:
            try:
                # Resolve hostname to IP
                ip = socket.gethostbyname(hostname)

                if is_private_ip(ip):
                    logger.warning(f"SSRF Protection: URL resolves to private IP: {hostname} -> {ip}")
                    return False, f"URL resolves to private/reserved IP address"
            except socket.gaierror as e:
                # DNS resolution failed
                logger.warning(f"SSRF Protection: Could not resolve hostname: {hostname}")
                return False, f"Could not resolve hostname: {hostname}"

        return True, ""

    except Exception as e:
        logger.error(f"SSRF Protection: URL validation error: {e}")
        return False, f"Invalid URL: {str(e)}"


def validate_url_for_download(url: str) -> Tuple[bool, str]:
    """
    Validate a URL specifically for file downloads.

    This is a convenience wrapper around validate_url with strict settings.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    return validate_url(url, check_domain=True, check_ip=True)


def validate_url_permissive(url: str) -> Tuple[bool, str]:
    """
    Validate a URL with permissive settings.

    Only checks for private IPs, does not check domain allowlist.
    Use for situations where any public URL should be allowed.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    return validate_url(url, check_domain=False, check_ip=True)
