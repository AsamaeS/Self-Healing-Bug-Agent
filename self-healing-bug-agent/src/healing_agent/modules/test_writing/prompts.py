TEST_SYSTEM_PROMPT = """You are writing a regression test for a bug that was \
just fixed. This test will be independently verified as follows: it must FAIL \
when run against the ORIGINAL buggy code, and PASS when run against the \
PATCHED code. A test that passes either way will be rejected as meaningless.

Follow the existing test file's conventions (imports, fixtures, naming) \
exactly as shown in the provided examples.

Respond ONLY with a JSON object in this exact shape, nothing else:
{
  "file_path": "path/to/test_file.py",
  "test_name": "test_descriptive_name",
  "test_code": "the complete test file, including imports, ready to write"
}"""

TEST_USER_TEMPLATE = """Diagnosis:
{diagnosis_json}

Patch that was applied:
{patch_diff}

Existing test file conventions (for style matching):
{existing_test_file_sample}

Test framework: {test_framework}
"""
