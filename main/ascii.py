# Simple ASCII helpers. Keep it dependency free.
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDER = "\033[4m"

FG_GREEN = "\033[32m"
FG_RED = "\033[31m"
FG_YELLOW = "\033[33m"
FG_CYAN = "\033[36m"
FG_MAGENTA = "\033[35m"
FG_BLUE = "\033[34m"
FG_WHITE = "\033[37m"

def banner(text: str) -> str:
    line = "=" * (len(text) + 4)
    return f"{FG_CYAN}{line}\n| {text} |\n{line}{RESET}"

def speech_bubble(text: str) -> str:
    lines = text.splitlines() or ["..."]
    width = max(len(l) for l in lines)
    top = "  " + "_" * (width + 2)
    body = "\n".join([f"< {l.ljust(width)} >" for l in lines])
    bottom = "  " + "-" * (width + 2)
    tail = "    \\\n     \\"
    return f"{FG_YELLOW}{top}\n{body}\n{bottom}\n{tail}{RESET}"

def face_happy() -> str:
    return FG_GREEN + r"( ＾▽＾)" + RESET

def face_grump() -> str:
    return FG_RED + r"( ಠ_ಠ )" + RESET

def trophy_panel(winner: str, quote: str) -> str:
    star = FG_YELLOW + "★" + RESET
    box_top = "╔" + "═" * 38 + "╗"
    box_mid = f"║ President: {winner}".ljust(39) + "║"
    box_quote = f"║ \"{quote}\"".ljust(39) + "║"
    box_bottom = "╚" + "═" * 38 + "╝"
    return f"{star} {BOLD}RESULTS{RESET}\n{box_top}\n{box_mid}\n{box_quote}\n{box_bottom}"
