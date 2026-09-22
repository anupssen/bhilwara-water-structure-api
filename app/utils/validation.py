def validate_subdistrict(subdistrict: str) -> str:
    """Strip whitespace and require a non-empty subdistrict name."""
    subdistrict = (subdistrict or "").strip()
    if not subdistrict:
        raise ValueError("subdistrict must not be empty")
    return subdistrict