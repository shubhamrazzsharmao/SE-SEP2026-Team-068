"""Logging for debugging: who called what, and what they did.

Everything goes to the "contentflow" logger and is printed in the uvicorn terminal.
Set LOG_LEVEL in .env (DEBUG, INFO, WARNING). Tokens and passwords are never logged.
"""
import logging

log = logging.getLogger("contentflow")


def setup(level: str) -> None:
    if not log.handlers:  # create_app() can run more than once (tests, --reload)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s [contentflow] %(message)s",
                                               datefmt="%H:%M:%S"))
        log.addHandler(handler)
        log.propagate = False
    log.setLevel(level.upper())


def who(user) -> str:
    """'name <email> (id)' for a User, or 'anonymous'."""
    if user is None:
        return "anonymous"
    return f"{user.name} <{user.email}> ({user.id})"


def short(value, limit: int = 200) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"
