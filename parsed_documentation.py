"""Represent documentation parsed from HTML."""

from dataclasses import dataclass
from enum import Enum


class EntityType(str, Enum):
    """Represent the type of entity in the C documentation."""

    FUNCTION = "function"
    MACRO = "macro"
    TYPE = "type"
    OTHER = "other"


@dataclass(frozen=True)
class FunctionParameter:
    """Represent a function parameter in the C documentation.

    Attributes:
        name (str): The parameter name.
        description (str): The description of the parameter.
    """

    name: str
    description: str


@dataclass(frozen=True)
class ParsedDocumentation:
    """Represent structured documentation parsed from the C HTML documentation.

    Attributes:
        entity_type (EntityType): The type of the entity parsed from the HTML.
        header_name (str): The name of the header file in which the entity is declared.
        description (str): The description parsed from the HTML.
        parameters (list[FunctionParameter]): The documentation for the function parameters,
            empty for all entities except for functions.
        return_value_description (str): The description of the return value.
    """

    entity_type: EntityType
    header_name: str
    description: str
    parameters: list[FunctionParameter]
    return_value_description: str
