#!/usr/bin/env python

"""Entry point to parsing HTML DevDocs C documentation."""

import argparse
import json
import re
from dataclasses import asdict
from pathlib import Path

from bs4 import BeautifulSoup

from parsed_documentation import EntityType, FunctionParameter, ParsedDocumentation


def main() -> None:
    """Entry point to parsing HTML DevDocs C documentation."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Parse HTML DevDocs C documentation into JSON.",
    )
    parser.add_argument(
        dest="index_file",
        type=str,
        help="The path to the index file for the DevDocs documentation.",
    )

    parser.add_argument(
        "--exclude-type",
        dest="exclude_types",
        type=EntityType,
        choices=list(EntityType),
        action="append",
        default=[],
        metavar="TYPE",
        help=(
            "Exclude entries of this type from output. Can be repeated. "
            f"Choices: {[e.value for e in EntityType]}"
        ),
    )

    args = parser.parse_args()
    entity_to_html_file = _get_named_entity_to_html_file(args.index_file)
    entity_to_documentation = {
        entity: asdict(parsed_doc)
        for entity, path_to_html in entity_to_html_file.items()
        if (parsed_doc := _parse_documentation(path_to_html))
        and parsed_doc.entity_type not in args.exclude_types
    }

    with Path("parsed_documentation.json").open(mode="w+") as f:
        f.write(json.dumps(entity_to_documentation, ensure_ascii=False))


def _get_named_entity_to_html_file(path_to_index: str) -> dict[str, str]:
    """Return the mapping of named entities (e.g., functions, macros) to their HTML files.

    Args:
        path_to_index (str): Path to the index.json file.

    Returns:
        dict[str, str]: The mapping of named entities to their HTML files.
    """
    entity_to_html_file = {}
    doc_index = Path(path_to_index)
    index = json.loads(doc_index.read_text(encoding="utf-8"))
    for entry in index["entries"]:
        entity = entry["name"]
        entity_to_html_file[entity] = _canonicalize_path(entry["path"])
    return entity_to_html_file


def _canonicalize_path(entry_file_name: str) -> str:
    """Return the canonicalized path from the entry file name.

    The index file displays non-absolute paths and drops the `.html` extension.

    Args:
        entry_file_name (str): The entry file name.

    Returns:
        str: The canonicalized entry file name.
    """
    return f"./data/{entry_file_name}.html"


def _parse_documentation(path_to_entry_html: str) -> ParsedDocumentation | None:
    """Return the documentation parsed from from an entry's HTML page.

    Args:
        path_to_entry_html (str): The path to the entry HTML.

    Returns:
        ParsedDocumentation | None: The documentation parsed from an entry's HTML page, or None
            if parsing fails.
    """
    html = BeautifulSoup(Path(path_to_entry_html).read_text(encoding="utf-8"), "html.parser")

    first_p = html.find("p")
    if not first_p:
        return None

    header_component = html.find(class_="t-dsc-header")
    header = _get_header(header_component)

    desc_parts = []
    for sibling in [first_p, *first_p.find_next_siblings()]:
        if sibling.name == "h3":
            break
        if sibling.name == "p":
            desc_parts.append(_get_text(sibling))
    description = " ".join(desc_parts)

    dcl = html.select_one("tr.t-dcl pre")
    if dcl is None:
        entity_type = EntityType.OTHER
    elif "(" in dcl.get_text():
        entity_type = EntityType.FUNCTION
    elif "#define" in dcl.get_text():
        entity_type = EntityType.MACRO
    else:
        entity_type = EntityType.TYPE

    parameters = []
    for row in html.select("tr.t-par"):
        cols = row.find_all("td")
        if len(cols) >= 3:
            parameters.append(
                FunctionParameter(
                    name=cols[0].get_text(strip=True),
                    description=_get_text(cols[2]),
                )
            )

    return_value_description = ""
    return_h3 = html.find("h3", id="Return_value")
    if return_h3:
        parts = []
        for sibling in return_h3.find_next_siblings():
            if sibling.name == "h3":
                break
            if sibling.name == "p":
                parts.append(_get_text(sibling))
        return_value_description = " ".join(parts)

    return ParsedDocumentation(
        entity_type=entity_type,
        header_name=header,
        description=description,
        parameters=parameters,
        return_value_description=return_value_description,
    )


def _get_text(tag) -> str:
    """Return text from a BeautifulSoup tag, preserving spaces around inline elements.

    BeautifulSoup's default get_text() strips tags without inserting spaces. For example, the text
    'If <code>x</code> is' is converted into 'Ifxis'. Using separator=' ' inserts a space at every
    tag boundary; collapsing runs of spaces restores natural readability.

    Args:
        tag (str): The tag from which to return text.

    Returns:
        str: Text from a BeautifulSoup tag, preserving spaces around inline elements.
    """
    return re.sub(
        r" ([.,;:!?)])",
        r"\1",
        re.sub(r" {2,}", " ", tag.get_text(separator=" ", strip=True)),
    )


def _get_header(header_desc_row) -> str:
    """Return the header from a header row component.

    The header row component is a table row that matches the format below:

        <tr class="t-dsc-header">
            <th colspan="2"> Defined in header <code>&lt;locale.h&gt;</code>  </th>
        </tr>

    This function returns the part from the row between the <code> blocks. E.g., "locale.h" for
    the example above.

    Args:
        header_desc_row: The header description row.

    Returns:
        str: The name of the header parsed from the header description row.
    """
    if not header_desc_row:
        return ""
    first_heading = header_desc_row.find("th")
    if not first_heading:
        return ""
    header_matches = re.findall(r"<([^<>]*)>", _get_text(first_heading))
    if not header_matches:
        return ""
    return header_matches[0]


if __name__ == "__main__":
    main()
