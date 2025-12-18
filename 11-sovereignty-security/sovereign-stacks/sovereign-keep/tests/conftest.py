import pytest
from src.analysis import SemanticAuditor, get_embedding_model

@pytest.fixture(scope="session")
def model():
    """Load model once per test session."""
    return get_embedding_model()

@pytest.fixture(scope="session")
def auditor(model):
    """Create auditor once per test session (uses singleton model)."""
    return SemanticAuditor(keep_client=None)
