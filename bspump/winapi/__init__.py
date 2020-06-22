"""
The `winapi` module works only on Windows based systems.
"""

from .event import WinEventSource

__all__ = (
	'WinEventSource',
)
