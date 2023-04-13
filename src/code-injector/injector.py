from typing import Optional


def inject_to_content(
    content_to_inject: str, content: str, start_line_str: Optional[str] = None
):
    """Injects content to a file at a specific line."""
    new_content = content
    # inject content
    stripped_content = "\n".join([line.strip() for line in new_content])
    inject_index = stripped_content.index(start_line_str) if start_line_str else -1
    if inject_index > -1:
        new_content.insert(inject_index, content_to_inject)
    else:
        new_content.append(content_to_inject)

    return new_content
