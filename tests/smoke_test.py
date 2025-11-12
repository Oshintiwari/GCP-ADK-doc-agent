from adk_app.pipeline import run_pipeline

def test_smoke():
    # Place real PDFs in data/ to run this meaningfully.
    resp = run_pipeline([], "What is the main topic?")
    assert resp.query
    assert isinstance(resp.logs, list)
