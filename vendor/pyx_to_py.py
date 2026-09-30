"""Convert IndicTransToolkit processor.pyx (Cython) to pure Python.

Part of the vendoring provenance for vendor/IndicTransToolkit/ (see that
directory's README.md). Kept so the port can be reproduced from the upstream
clone (vendor/itto-src/, gitignored):

    python vendor/pyx_to_py.py vendor/itto-src/IndicTransToolkit/processor.pyx vendor/IndicTransToolkit/processor.py

Mechanical, semantics-preserving transformation:
  - `cdef class X:`            -> `class X:`
  - class-level `cdef ...` declarations (no assignment) -> removed
  - `def __cinit__`            -> `def __init__`
  - `cdef <ret> f(...) except *:` / `cpdef <ret> f(...)` -> `def f(...):` with param types stripped
  - local `cdef <type> name = expr` -> `name = expr`
  - local bare `cdef <type> name`   -> line removed (assigned before use in body)
No logic lines are altered.
"""
import re
import sys

SRC = sys.argv[1]
DST = sys.argv[2]

TYPE = (
    r"(?:List\[[^\]]*\]|Dict\[[^\]]*\]|Union\[[^\]]*\]|Tuple\[[^\]]*\]|"
    r"str|list|dict|tuple|set|frozenset|int|float|bool|bytes|bint|object|double|long)"
)

# def-like header: (cdef|cpdef|def) [TYPE] name(
DEF_RE = re.compile(rf"^(cdef|cpdef|def)\s+(?:{TYPE}\s+)?([A-Za-z_]\w*)\s*\(")
# assignment declaration: cdef [public|readonly] TYPE <rest with '='>
ASSIGN_RE = re.compile(rf"^(cdef|cpdef)\s+(?:public\s+|readonly\s+)?{TYPE}\s+(.+)$")
# any cdef/cpdef declaration line
DECL_RE = re.compile(r"^(cdef|cpdef)\b")


def split_top_level(params: str):
    """Split params on top-level commas (ignores commas inside [] () {})."""
    parts, depth, cur = [], 0, ""
    for ch in params:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def strip_param(p: str) -> str:
    """'str tgt_lang=None,' -> 'tgt_lang=None,' ; 'bint x' -> 'x' ; 'self,' -> 'self,'"""
    p = p.strip()
    comma = ""
    if p.endswith(","):
        comma, p = ",", p[:-1].strip()
    m = re.fullmatch(rf"(?:{TYPE}\s+)?([A-Za-z_]\w*)(\s*=\s*.+)?", p)
    if not m:
        raise ValueError(f"unparseable param: {p!r}")
    return m.group(1) + (m.group(2) or "") + comma


def strip_params_block(params: str) -> str:
    return ", ".join(strip_param(p) for p in split_top_level(params))


def convert_line(line: str, out: list, state: dict) -> None:
    mode = state["mode"]
    indent = len(line) - len(line.lstrip())
    s = line.strip()

    # ---- inside a multi-line signature ----
    if mode == "sig":
        if ")" in s:
            head, _, _tail = s.partition(")")
            head = head.strip().rstrip(",")
            param_txt = strip_param(head) if head else ""
            out.append(" " * indent + param_txt + (":" if param_txt.endswith(",") else "):"))
            state["mode"] = None
        else:
            out.append(" " * indent + strip_param(s))
        return

    # ---- class declaration ----
    if s.startswith("cdef class "):
        out.append(line.replace("cdef class ", "class ", 1))
        return

    # ---- def-like header (cdef/cpdef/def) ----
    m = DEF_RE.match(s)
    if m and "(" in s:
        name = m.group(2)
        if name == "__cinit__":
            name = "__init__"
        open_idx = s.index("(", m.start())
        if ")" in s:
            # single-line signature; strip trailing 'except *:' etc.
            params = s[open_idx + 1 : s.rindex(")")]
            out.append(" " * indent + f"def {name}({strip_params_block(params)}):")
        else:
            out.append(" " * indent + f"def {name}(")
            state["mode"] = "sig"
        return

    # ---- plain cdef/cpdef lines ----
    if DECL_RE.match(s):
        if re.search(r"(?<![=!<>])=(?!=)", s):
            m2 = ASSIGN_RE.match(s)
            if not m2:
                raise ValueError(f"unparseable assignment: {line!r}")
            out.append(" " * indent + m2.group(2))
        # bare declaration (no assignment): drop the line
        return

    # ---- ordinary line ----
    out.append(line)


def main():
    with open(SRC, encoding="utf-8") as f:
        src = f.read()
    lines = src.split("\n")
    out, state = [], {"mode": None}
    for line in lines:
        convert_line(line, out, state)
    if state["mode"] is not None:
        raise ValueError("unterminated signature")
    result = "\n".join(out)
    with open(DST, "w", encoding="utf-8", newline="\n") as f:
        f.write(result)
    # verify it is valid Python
    compile(result, DST, "exec")
    print(f"OK: {DST} ({len(result)} bytes) compiles")


if __name__ == "__main__":
    main()
