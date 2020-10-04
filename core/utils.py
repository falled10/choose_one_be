from humps import camelize


def to_camel(string: str) -> str:
    """Camelize all incoming and returned data from pydantic schemas"""
    return camelize(string)
