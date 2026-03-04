"""Placeholder tests so pytest can run. Expand with triage tests per plan."""

import pytest


def test_placeholder():
    """Pytest can discover and run tests in tests/."""
    assert True


def test_refinery_import():
    """Package is importable."""
    from refinery import DocumentProfile, LanguageInfo, run_triage, RefineryTriageError

    assert DocumentProfile is not None
    assert LanguageInfo is not None
    assert run_triage is not None
    assert RefineryTriageError is not None
