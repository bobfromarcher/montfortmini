"""Retain real identity pixels up to the native Qwen VAE reference budget.

This is bounded input preparation, not super-resolution or face restoration.
Legacy study helpers remain unchanged so their runtime hashes still reproduce.
"""
import math
from reference_alignment import identity_canvas as legacy_identity_canvas

MAX_IDENTITY_PIXELS = 1024 * 1024


def identity_canvas(width, height):
    if type(width) is not int or type(height) is not int or min(width, height) <= 0:
        raise ValueError('Identity dimensions must be positive integers')
    if width * height > 16_777_216:
        raise ValueError('Identity image exceeds the decoded input limit')
    w, h = legacy_identity_canvas(width, height)
    # Integer enlargement holds the legacy aspect ratio and native Qwen token
    # geometry constant. The caller resizes ORIGINAL pixels directly once.
    factor = max(1, math.floor(min(math.sqrt(MAX_IDENTITY_PIXELS / (w * h)),
                                   math.sqrt(width * height / (w * h)))))
    return w * factor, h * factor
