"""Assembla visualizer/index.html da src/.

    python3 visualizer/build.py

Inserisce nel template: il tracer Python, gli esempi, il CSS di CodeMirror
e una traccia già calcolata del primo esempio (così la pagina mostra subito
un'animazione mentre Pyodide si carica).
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src"
sys.path.insert(0, str(SRC))

import tracer  # noqa: E402
from examples import EXAMPLES  # noqa: E402


def js_json(obj):
    # evita che "</script>" dentro una stringa chiuda il tag
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main():
    template = (SRC / "template.html").read_text()
    tracer_src = (SRC / "tracer.py").read_text()
    cm_css = (SRC / "codemirror.css").read_text()
    examples = [{"title": t, "tag": g, "code": c} for t, g, c in EXAMPLES]
    first = json.loads(tracer.run_trace(examples[0]["code"], 2000))

    out = (template
           .replace("/*@CODEMIRROR_CSS@*/", cm_css)
           .replace("@TRACER_PY@", tracer_src.replace("</", "<\\/"))
           .replace("/*@EXAMPLES@*/null", js_json(examples))
           .replace("/*@FIRST_TRACE@*/null", js_json(first)))
    for marker in ("@CODEMIRROR_CSS@", "@TRACER_PY@", "@EXAMPLES@", "@FIRST_TRACE@"):
        assert marker not in out, marker
    (HERE / "index.html").write_text(out)
    print(f"index.html scritto ({len(out) // 1024} KB, {len(first['steps'])} passi nell'esempio iniziale)")


if __name__ == "__main__":
    main()
