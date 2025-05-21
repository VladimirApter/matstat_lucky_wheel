#!/usr/bin/env python3
"""Shared configuration constants for Lucky Wheel rendering and animation."""

# Canvas / drawing
CANVAS_PX   = 1000
WHEEL_R     = 1.32
LABEL_R     = WHEEL_R * 0.65
FONT_SZ     = 12

# Static overlay (rim + pointer)
RIM_OUTSET  = 0.10
EDGE_COLOR  = "#d8d8d8"
POINTER_IN  = 0.025
POINTER_HALF= 0.065

# Motion parameters (kept in sync with animation.js)
ACCEL_MS     = 1500   # acceleration phase length (ms)
DECEL_MS     = 10000  # deceleration phase length (ms)
CONST_MAX_MS = 4000   # maximum constant‑speed phase (ms)
MAX_OMG_MS   = 0.015  # peak angular velocity (rad / ms)
DECEL_K      = 5      # exponential damping coefficient
