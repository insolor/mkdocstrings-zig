import re


def _parse_zig_code(code: str) -> dict[str, list[dict]]:
    """
    A minimal Zig parser that extracts:
    - Module documentation (`//!`)
    - Declaration documentation (`///`)
    - Functions (`fn`)
    - Constants (`const`)
    - Structs (`struct`)
    """
    lines = code.split("\n")
    parsed_data = {
        "module_docs": [],  # For //! comments
        "functions": [],
        "constants": [],
        "structs": [],
    }

    current_doc = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Handle module documentation (//!)
        if line.startswith("//!"):
            # Collect all consecutive module doc lines
            while i < len(lines) and lines[i].strip().startswith("//!"):
                parsed_data["module_docs"].append(lines[i].strip()[3:].strip())
                i += 1
            continue

        # Handle declaration documentation (///)
        if line.startswith("///"):
            # Collect all consecutive doc lines
            doc_lines = []
            while i < len(lines) and lines[i].strip().startswith("///"):
                doc_lines.append(lines[i].strip()[3:].strip())
                i += 1

            # Skip empty lines between docs and declaration
            while i < len(lines) and not lines[i].strip():
                i += 1

            if i >= len(lines):
                break

            line = lines[i].strip()
            current_doc = "\n".join(doc_lines)

            # Parse functions
            if line.startswith("fn ") or " fn " in line:
                match = re.match(r"fn\s+([a-zA-Z0-9_]+)\s*\(", line)
                if match:
                    parsed_data["functions"].append(
                        {
                            "name": match.group(1),
                            "doc": current_doc,
                        }
                    )

            # Parse constants
            elif line.startswith("const "):
                match = re.match(r"const\s+([a-zA-Z0-9_]+)\s*=", line)
                if match:
                    if "= struct" in line:
                        # Handle structs
                        parsed_data["structs"].append(
                            {
                                "name": match.group(1),
                                "doc": current_doc,
                            }
                        )
                    else:
                        # Regular constants
                        parsed_data["constants"].append(
                            {
                                "name": match.group(1),
                                "doc": current_doc,
                            }
                        )

            current_doc = []
            continue

        i += 1

    # Join module docs into single string
    if parsed_data["module_docs"]:
        parsed_data["module_docs"] = "\n".join(parsed_data["module_docs"])
    else:
        parsed_data.pop("module_docs")

    return parsed_data
