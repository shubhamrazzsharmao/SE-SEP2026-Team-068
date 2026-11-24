"""Shared test constants and matchers (kept out of conftest so tests can import them)."""

TEST_SECRET = "contentflow-test-secret-0123456789abcdef"

MISSING = object()
PRESENT = object()  # expected: "field exists and is not null"


class Contains(str):
    """Expected value matcher: the actual string must contain this text."""


BRIEF = {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit",
         "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material",
         "platforms": ["blog", "linkedin", "facebook", "instagram"]}
