# SPDX-License-Identifier: Apache-2.0
import pytest


class _FakeLLM:
    def __init__(self, responses):
        self._r = list(responses)
        self.calls = []

    def complete(self, prompt, system=""):
        self.calls.append(prompt)
        return self._r.pop(0) if self._r else ""


class _FakeConnector:
    def __init__(self, responses):
        self._r = list(responses)

    def ask(self, prompt):
        return self._r.pop(0) if self._r else ""


@pytest.fixture
def fake_llm():
    return lambda responses: _FakeLLM(responses)


@pytest.fixture
def fake_connector():
    return lambda responses: _FakeConnector(responses)
