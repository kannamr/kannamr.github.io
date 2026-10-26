# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Single-process admission control; requests never wait in an application queue."""
import time


class Admission:
    def __init__(self, concurrency, rate, burst, clock=time.monotonic):
        self.concurrency = concurrency
        self.rate = rate / 60.0
        self.burst = burst
        self.tokens = float(burst)
        self.active = 0
        self.clock = clock
        self.updated = clock()

    def acquire(self):
        # No await points: this transition is atomic within the single event loop.
        now = self.clock()
        self.tokens = min(self.burst, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if self.tokens < 1:
            return 'rate'
        if self.active >= self.concurrency:
            return 'capacity'
        self.tokens -= 1
        self.active += 1
        return None

    def release(self):
        self.active -= 1
