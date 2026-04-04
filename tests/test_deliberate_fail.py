"""Deliberately failing test to demonstrate CI blocking a deploy."""


def test_this_should_fail():
    assert 1 == 2, "This test intentionally fails to demonstrate blocked deploys"
