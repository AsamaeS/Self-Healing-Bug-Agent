from pydantic import BaseModel


class TestProposal(BaseModel):
    """A proposed regression test -- not yet verified. The verification
    module is responsible for confirming it fails pre-patch and passes
    post-patch before it is trusted."""
    file_path: str
    test_name: str
    test_code: str
