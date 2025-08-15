import sys
import types
import pytest


@pytest.fixture(autouse=True, scope="session")
def stub_google_module():
    # Provide a minimal stub for google.generativeai to avoid external dependency in tests
    google = types.ModuleType("google")
    generativeai = types.ModuleType("google.generativeai")

    class _Model:
        async def generate_content_async(self, prompt):
            class _Resp:
                text = "stubbed response"
            return _Resp()

    def configure(**kwargs):
        return None

    def GenerativeModel(name):
        return _Model()

    generativeai.configure = configure
    generativeai.GenerativeModel = GenerativeModel
    google.generativeai = generativeai
    sys.modules.setdefault("google", google)
    sys.modules.setdefault("google.generativeai", generativeai)
    return True


