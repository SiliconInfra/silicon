# BGP ASN bounds
BGP_ASN_MIN = 1
BGP_ASN_MAX = 2 ** 32 - 1

#
# VRFs
#

# Per RFC 4364 section 4.2, a route distinguisher may be encoded as one of the following:
#   * Type 0 (16-bit AS number : 32-bit integer)
#   * Type 1 (32-bit IPv4 address : 16-bit integer)
#   * Type 2 (32-bit AS number : 16-bit integer)
# 21 characters are sufficient to convey the longest possible string value (255.255.255.255:65535)
VRF_RD_MAX_LENGTH = 21

#
# Prefixes
#
PREFIX_LENGTH_MIN = 1
PREFIX_LENGTH_MAX = 127  # IPv6
