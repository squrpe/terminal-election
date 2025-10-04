import argparse, os, random, math
from typing import List, Tuple, Dict
from .models import Candidate, Issue, TRAIT_CATEGORIES
from . import ascii as art
from . import io_utils

def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="terminal-election", description="Chaotic satirical election simulator")
    p.add_argument("--data", default="data", help="Path to input txt files")
    p.add_argument("--build", default="build", help="Path to build folder for JSON and CSV outputs")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible runs")
    p.add_argument("--rounds", type=int, default=6, help="How many issues per session")
    p.add_argument("--pref", type=float, default=1.0, help="Preference strength multiplier")
    p.add_argument("--chaos", type=float, default=0.1, help="Probability of flipping a vote at random [0..1]")
    p.add_argument("--bias", type=float, default=0.0, help="Baseline skew, positive favours For, negative favours Against")
    p.add_argument("--serious-mult", type=float, default=1.0, help="Weight multiplier for serious issues")
    p.add_argument("--funny-mult", type=float, default=1.0, help="Weight multiplier for funny issues")
    p.add_argument("--mixed-mult", type=float, default=1.0, help="Weight multiplier for mixed issues")
    p.add_argument("--justify", type=int, default=2, help="How many candidates justify themselves per round")
    p.add_argument("--cands", type=int, default=5, help="Limit number of candidates to include (0 means all)")
    p.add_argument("--no-colour", action="store_true", help="Disable coloured output")
    return p.parse_args(argv)

def colourise(disable: bool):
    if disable:
        # Wipe ANSI codes by overriding module constants
        for name in ["RESET","BOLD","DIM","UNDER","FG_GREEN","FG_RED","FG_YELLOW","FG_CYAN","FG_MAGENTA","FG_BLUE","FG_WHITE"]:
            setattr(art, name, "")
    return art

def load_world(args):
    io_utils.ensure_build_jsons(args.data, args.build)
    names, issues_j, reasons, quotes = io_utils.load_sources(args.build)
    # Convert issues dicts to objects
    issues = [Issue(**d) for d in issues_j]
    return names, issues, reasons, quotes

def make_candidates(names: List[str], quotes: List[str], rng: random.Random, limit: int) -> List[Candidate]:
    rng.shuffle(names)
    chosen = names if limit == 0 else names[:limit]
    return [Candidate.random(name, rng.choice(quotes), rng) for name in chosen]

def issue_effect(issue: Issue, candidate: Candidate, pref: float) -> float:
    # Sum trait alignment over tags
    if not issue.tags:
        return 0.0
    s = sum(candidate.traits.get(tag, 0) for tag in issue.tags)
    return s * pref

def decide_vote(base_alignment: float, bias: float, chaos: float, rng: random.Random) -> Tuple[str, bool]:
    # Positive means tilt to For
    tilt = base_alignment + bias
    vote_for = tilt >= 0
    # chaos flip
    if rng.random() < chaos:
        vote_for = not vote_for
    return ("For" if vote_for else "Against"), vote_for == (base_alignment >= 0)

def type_multiplier(issue_type: str, serious_mult: float, funny_mult: float, mixed_mult: float) -> float:
    if issue_type == "serious":
        return serious_mult
    if issue_type == "funny":
        return funny_mult
    return mixed_mult

def run_round(round_idx: int, issue: Issue, candidates: List[Candidate], reasons: List[str], cfg, rng: random.Random):
    print(art.banner(f"Round {round_idx+1}: {issue.text}"))
    wmult = type_multiplier(issue.type, cfg.serious_mult, cfg.funny_mult, cfg.mixed_mult)
    votes = []
    for c in candidates:
        align = issue_effect(issue, c, cfg.pref)
        vote, aligned = decide_vote(align, cfg.bias, cfg.chaos, rng)
        # Score: aligned gets +weight, misaligned gets -weight
        delta = (issue.weight * wmult) * (1.0 if aligned else -1.0)
        c.score += delta
        votes.append((c, vote, aligned, delta))

    # Reveal summary
    for_count = sum(1 for _, v, _, _ in votes if v == "For")
    against_count = len(votes) - for_count
    print(f"{art.FG_GREEN}For: {for_count}{art.RESET} | {art.FG_RED}Against: {against_count}{art.RESET}")

    # Pick some to justify, try to include one from each side if possible
    rng.shuffle(votes)
    chosen = []
    side_for = [t for t in votes if t[1] == "For"]
    side_against = [t for t in votes if t[1] == "Against"]
    if side_for:
        chosen.append(rng.choice(side_for))
    if side_against and len(chosen) < cfg.justify:
        chosen.append(rng.choice(side_against))
    while len(chosen) < min(cfg.justify, len(votes)):
        # fill any
        extra = rng.choice(votes)
        if extra not in chosen:
            chosen.append(extra)

    for (c, v, _aligned, _delta) in chosen:
        reason = rng.choice(reasons)
        face = art.face_happy() if v == "For" else art.face_grump()
        print(face, art.speech_bubble(f"{c.name}: {reason}"))

    # Prepare CSV rows
    rows = []
    for c, v, aligned, delta in votes:
        rows.append((round_idx+1, issue.text, c.name, v, str(aligned), f"{delta:.2f}"))
    return rows

def scoreboard(candidates: List[Candidate]):
    print(art.banner("Final Scoreboard"))
    ranked = sorted(candidates, key=lambda c: c.score, reverse=True)
    print(f"{'Rank':<6}{'Name':<16}{'Score':>8}")
    for i, c in enumerate(ranked, 1):
        print(f"{i:<6}{c.name:<16}{c.score:>8.2f}")
    return ranked

def main(argv=None):
    args = parse_args(argv)
    rng = random.Random(args.seed)
    colourise(args.no_colour)
    names, issues, reasons, quotes = load_world(args)
    candidates = make_candidates(names, quotes, rng, args.cands)

    print(art.banner("Welcome to TERMINAL ELECTION"))
    print(f"Candidates: {', '.join(c.name for c in candidates)}")
    input("Press Enter to begin...")

    # Choose rounds
    rng.shuffle(issues)
    chosen_issues = issues[:args.rounds]

    all_rows = []
    for idx, issue in enumerate(chosen_issues):
        all_rows.extend(run_round(idx, issue, candidates, reasons, args, rng))
        input("Press Enter for next round...")

    ranked = scoreboard(candidates)
    winner = ranked[0]
    print()
    print(art.trophy_panel(winner.name, winner.quote))

    csv_path = io_utils.export_votes_csv(all_rows, args.build)
    print(f"\nVotes exported to: {csv_path}")

if __name__ == "__main__":
    main()
