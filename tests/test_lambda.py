import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_handler_returns_200(monkeypatch):
    import lambda_function
    monkeypatch.setattr(lambda_function, "fetch_matches", lambda: [{"match_id": 1}])
    monkeypatch.setattr(lambda_function, "fetch_standings", lambda: [{"group": "A"}])
    monkeypatch.setattr(lambda_function, "save_to_s3", lambda data: "worldcup/2026/06/01/12-00-00.json")
    result = lambda_function.handler({}, {})
    assert result["statusCode"] == 200

def test_handler_returns_500_on_error(monkeypatch):
    import lambda_function
    monkeypatch.setattr(lambda_function, "fetch_matches", lambda: (_ for _ in ()).throw(Exception("timeout")))
    result = lambda_function.handler({}, {})
    assert result["statusCode"] == 500
