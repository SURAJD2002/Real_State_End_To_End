"""
Planwise Enterprise — Deterministic buildingSMART IFC GUID Generator
Milestone 1 — BIM / IFC Professionalization
Conforms to RFC 4122 UUIDv5 and buildingSMART 22-character compressed base64 specification.
"""

import uuid
import string
from functools import reduce
from typing import Union

# Standard buildingSMART 64-character alphabet for IFC GloballyUniqueId
IFC_BASE64_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_$"

# Authoritative Planwise Enterprise namespace UUID for RFC 4122 UUIDv5 generation
NAMESPACE_PLANWISE = uuid.uuid5(uuid.NAMESPACE_DNS, "planwise.enterprise.ifc")


def compress_guid(guid_input: Union[uuid.UUID, str]) -> str:
    """
    Compresses a 128-bit UUID into buildingSMART's 22-character base64 format.
    Algorithm conforms to ISO 16739-1 / buildingSMART reference implementation.
    """
    if isinstance(guid_input, uuid.UUID):
        g = guid_input.hex
    else:
        g = str(guid_input).replace("-", "").strip()

    if len(g) != 32:
        raise ValueError(f"Expected 32-character hexadecimal UUID, got '{g}' (length {len(g)})")

    bs = [int(g[i : i + 2], 16) for i in range(0, len(g), 2)]

    def b64(v: int, length: int = 4) -> str:
        return "".join([IFC_BASE64_ALPHABET[(v // (64 ** i)) % 64] for i in range(length)][::-1])

    # 1 byte (2 chars) + 5 groups of 3 bytes (4 chars each) = 22 characters
    return "".join(
        [b64(bs[0], 2)] +
        [b64((bs[i] << 16) + (bs[i + 1] << 8) + bs[i + 2], 4) for i in range(1, 16, 3)]
    )


def expand_guid(ifc_guid: str) -> str:
    """
    Expands a 22-character buildingSMART IFC GUID back into standard 32-character hex UUID.
    Inverse of compress_guid.
    """
    if len(ifc_guid) != 22:
        raise ValueError(f"Expected 22-character IFC GUID, got '{ifc_guid}' (length {len(ifc_guid)})")

    def b64_decode(v_str: str) -> int:
        return reduce(lambda a, b: a * 64 + b, map(lambda c: IFC_BASE64_ALPHABET.index(c), v_str))

    bs = [b64_decode(ifc_guid[0:2])]
    for i in range(5):
        d = b64_decode(ifc_guid[2 + 4 * i : 6 + 4 * i])
        bs += [(d >> (8 * (2 - j))) % 256 for j in range(3)]

    return "".join(["%02x" % b for b in bs])


def generate_deterministic_ifc_guid(release_id: str, element_id: str) -> str:
    """
    Generates a deterministic 22-character IFC GUID using RFC 4122 UUIDv5.

    Requirements:
    - Same release + same element_id => identical IFC GUID
    - Different element_id => different IFC GUID
    - Repeated calls => 100% deterministic, zero randomness
    - Length == 22 characters
    """
    seed = f"{release_id}:{element_id}"
    u = uuid.uuid5(NAMESPACE_PLANWISE, seed)
    return compress_guid(u)
