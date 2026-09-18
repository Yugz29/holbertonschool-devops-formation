#!/usr/bin/env python3
"""Tests for HolbieBot."""

import unittest
from devops_bot import validate_energy


class TestValidateEnergy(unittest.TestCase):
    def test_normal_value(self):
        self.assertEqual(validate_energy(50), 50)

    def test_value_below_zero(self):
        self.assertEqual(validate_energy(-20), 0)

    def test_value_above_hundred(self):
        self.assertEqual(validate_energy(150), 100)

if __name__ == "__main__":
    unittest.main()
