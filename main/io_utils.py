import os, json, csv
from typing import List, Tuple
from .models import Candidate, Issue, TRAIT_CATEGORIES

def ensure_build_jsons(data_dir: str, build_dir: str):
    os.makedirs(build_dir, exist_ok=True)

    # names -> candidates.json requires quotes too
    names_path = os.path.join(data_dir, "names.txt")
    issues_path = os.path.join(data_dir, "issues.txt")
    reasons_path = os.path.join(data_dir, "reasons.txt")
    quotes_path = os.path.join(data_dir, "quotes.txt")

    # Basic existence checks
    for path in [names_path, issues_path, reasons_path, quotes_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required data file: {path}")

    # Convert to JSON containers but candidates are generated at runtime
    with open(issues_path, "r", encoding="utf-8") as f:
        issue_lines = [line.strip() for line in f if line.strip()]

    from .models import Issue
    issues = [Issue.from_line(line).__dict__ for line in issue_lines]

    with open(os.path.join(build_dir, "issues.json"), "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)

    # reasons
    with open(reasons_path, "r", encoding="utf-8") as f:
        reasons = [line.strip() for line in f if line.strip()]
    with open(os.path.join(build_dir, "reasons.json"), "w", encoding="utf-8") as f:
        json.dump(reasons, f, indent=2, ensure_ascii=False)

    # quotes
    with open(quotes_path, "r", encoding="utf-8") as f:
        quotes = [line.strip() for line in f if line.strip()]
    with open(os.path.join(build_dir, "quotes.json"), "w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=2, ensure_ascii=False)

    # names
    with open(names_path, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]
    with open(os.path.join(build_dir, "names.json"), "w", encoding="utf-8") as f:
        json.dump(names, f, indent=2, ensure_ascii=False)

def load_sources(build_dir: str):
    def load(name):
        with open(os.path.join(build_dir, name), "r", encoding="utf-8") as f:
            return json.load(f)
    names = load("names.json")
    issues = load("issues.json")
    reasons = load("reasons.json")
    quotes = load("quotes.json")
    return names, issues, reasons, quotes

def export_votes_csv(rows, build_dir: str):
    path = os.path.join(build_dir, "votes.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["round", "issue", "candidate", "vote", "aligned", "round_score"])
        for r in rows:
            writer.writerow(r)
    return path
