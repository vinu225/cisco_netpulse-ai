"""Unit test suite verifying fuzzy fault matching comparison logic in NetPulse AI evaluator."""

import pytest
from src.evaluator import _compare_faults


def test_compare_faults_exact():
    """Verify exact title match equality."""
    assert _compare_faults("Wrong IP Address", "Wrong IP Address") is True


def test_compare_faults_casing():
    """Verify case-insensitive string matching."""
    assert _compare_faults("wrong ip address", "Wrong IP Address") is True
    assert _compare_faults("WRONG IP ADDRESS", "wrong ip address") is True


def test_compare_faults_substring_alignment():
    """Verify substring containment evaluation."""
    assert _compare_faults("Predicted Case: Wrong IP Address", "Wrong IP Address") is True
    assert _compare_faults("Wrong IP Address", "Predicted Case: Wrong IP Address") is True


def test_compare_faults_mismatch():
    """Verify distinct fault titles return false."""
    assert _compare_faults("Wrong Subnet Mask", "Wrong IP Address") is False
    assert _compare_faults("DHCP Pool Missing", "Wrong DHCP Gateway") is False


def test_compare_faults_extended_sentence():
    """Verify phrase containment in detailed diagnostic responses."""
    assert _compare_faults("Identified issue: Wrong IP Address on host interface", "Wrong IP Address") is True
    assert _compare_faults("Wrong IP Address", "Identified issue: Wrong IP Address on host interface") is True