import json
import argparse
from pathlib import Path
from adk_app.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Ask questions about PDFs in a folder.")
    parser.add_argument("--q", "-q", required=True, help="Your natural language question")
    parser.add_argument("--data", default="data", help="Folder containing PDFs")
    parser.add_argument("--top-k", type=int, default=None, help="Override retrieval k")
    parser.add_argument("--show-logs", action="store_true", help="Print agent decision logs")
    parser.add_argument("--save-json", default=None, help="Path to save the JSON response")
    args = parser.parse_args()

    pdfs = sorted(str(p) for p in Path(args.data).glob("*.pdf"))
    if not pdfs:
        print(json.dumps({"error": f"No PDFs found in folder: {args.data}"}, indent=2))
        raise SystemExit(1)

    # Pass top_k to pipeline directly
    resp = run_pipeline(pdfs, args.q, top_k=args.top_k)

    payload = resp.model_dump()
    if args.show_logs and "logs" in payload:
        print("\n=== AGENT LOGS ===")
        for line in payload.get("logs", []):
            print(line)

    print(json.dumps(payload, indent=2))

    if args.save_json:
        out = Path(args.save_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nSaved JSON to {out}")

if __name__ == "__main__":
    main()
