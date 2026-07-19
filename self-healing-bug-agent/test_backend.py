
from fastapi.testclient import TestClient
from healing_agent.app import create_app

app = create_app()
client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_run():
    response = client.post("/api/v1/runs", json={
        "repo_full_name": "test/repo",
        "base_sha": "abc1234",  # 7 characters
        "bug_report": "Test bug",
        "trigger_type": "manual"  # lowercase
    })
    print("Create run response status:", response.status_code)
    print("Create run response json:", response.json())
    print("Create run response text:", response.text)
    assert response.status_code == 202
    data = response.json()
    assert "run_id" in data
    assert "status" in data


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    test_health_check()
    print("✓ Health check passed")
    test_create_run()
    print("✓ Create run passed")
    print("✅ All backend tests passed!")
