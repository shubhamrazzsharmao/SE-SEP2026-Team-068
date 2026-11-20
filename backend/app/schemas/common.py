"""Shared field types and validators for the request/response schemas."""
import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

Name150 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=5000)]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def clean_terms(v):
    if v is None:
        return v
    cleaned: list[str] = []
    for t in v:
        t = t.strip()
        if t and t not in cleaned:
            cleaned.append(t)
    if len(cleaned) > 50 or any(len(t) > 100 for t in cleaned):
        raise ValueError("At most 50 terms, each at most 100 characters.")
    return cleaned
