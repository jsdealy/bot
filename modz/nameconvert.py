def nameconvert(name: str) -> str:
    if name.startswith("lgularte"):
        return "louis"
    if name.startswith("patrickcamp"):
        return "patrick"
    if name.startswith("tomotheos"):
        return "tim"
    if name.startswith("jdealy"):
        return "justin"
    if name.startswith("mtbiz"):
        return "taylor"
    else:
        return name.lower()
