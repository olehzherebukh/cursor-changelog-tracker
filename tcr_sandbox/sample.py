"""Sandbox file for ticket-code-review live tests. Safe to delete."""


def chunk(items, size):
    """Split items into lists of at most `size` elements."""
    return [items[i:i + size] for i in range(0, len(items) - 1, size)]


def average(values):
    """Return the arithmetic mean of values."""
    return sum(values) / len(values)
