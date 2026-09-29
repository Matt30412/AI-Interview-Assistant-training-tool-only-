# Tracer per il visualizzatore SDA.
# Esegue il codice dell'utente con sys.settrace e registra, riga per riga,
# lo stack delle chiamate e tutti gli oggetti raggiungibili (heap).
import sys, io, json, math, time, types
from collections import deque, defaultdict, Counter, OrderedDict
import heapq, bisect, itertools, functools
from typing import List, Optional, Dict, Set, Tuple

USER_FILE = "<solution>"
SKIP_FRAMES = {"<genexpr>", "<lambda>", "<listcomp>", "<dictcomp>", "<setcomp>"}
MAX_ITEMS = 120        # elementi massimi serializzati per contenitore
MAX_HEAP = 400         # oggetti massimi per passo
MAX_STR = 200


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        return f"ListNode({self.val!r})"


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        return f"TreeNode({self.val!r})"


def build_list(values):
    """[1,2,3] -> 1 -> 2 -> 3"""
    head = None
    for v in reversed(list(values)):
        head = ListNode(v, head)
    return head


def build_tree(values):
    """Ordine per livelli come su LeetCode: [3,9,20,None,None,15,7]"""
    values = list(values)
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q = deque([root])
    i = 1
    while q and i < len(values):
        node = q.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            q.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            q.append(node.right)
        i += 1
    return root


def list_to_array(head):
    out, seen = [], set()
    while head is not None and id(head) not in seen:
        seen.add(id(head))
        out.append(head.val)
        head = head.next
    return out


HELPERS = {
    "ListNode": ListNode, "TreeNode": TreeNode,
    "build_list": build_list, "build_tree": build_tree, "list_to_array": list_to_array,
    "deque": deque, "defaultdict": defaultdict, "Counter": Counter, "OrderedDict": OrderedDict,
    "heapq": heapq, "bisect": bisect, "itertools": itertools, "functools": functools,
    "math": math, "List": List, "Optional": Optional, "Dict": Dict, "Set": Set, "Tuple": Tuple,
    "inf": math.inf,
}


class StepLimit(Exception):
    pass


class Recorder:
    def __init__(self, max_steps):
        self.max_steps = max_steps
        self.steps = []
        self.ids = {}       # id(obj) -> id stabile
        self.keep = []      # riferimenti tenuti vivi: evita il riuso degli id
        self.out = io.StringIO()
        self.stopped = False
        self.ops = 0
        self.t0 = time.time()
        self.max_seconds = 8
        self.calls = 0
        self.fids = {}      # id(frame) -> (numero di chiamata, frame)

    # ---------- serializzazione ----------
    def ref(self, obj):
        k = id(obj)
        if k not in self.ids:
            self.ids[k] = len(self.ids) + 1
            self.keep.append(obj)
        return self.ids[k]

    def enc(self, v, pending):
        if v is None:
            return ["N"]
        if isinstance(v, bool):
            return ["B", v]
        if isinstance(v, int):
            if abs(v) < 2 ** 53:
                return ["I", v]
            return ["F", repr(v)]
        if isinstance(v, float):
            if math.isfinite(v):
                return ["F", v]
            return ["F", repr(v)]
        if isinstance(v, str):
            return ["S", v if len(v) <= MAX_STR else v[:MAX_STR] + "…"]
        if isinstance(v, (types.FunctionType, types.MethodType, types.BuiltinFunctionType)):
            return ["X", f"funzione {getattr(v, '__name__', '?')}"]
        if isinstance(v, type):
            return ["X", f"classe {v.__name__}"]
        if isinstance(v, types.ModuleType):
            return ["X", f"modulo {v.__name__}"]
        if isinstance(v, (list, tuple, set, frozenset, dict, deque)) or hasattr(v, "__dict__") or hasattr(v, "__slots__"):
            pending.append(v)
            return ["R", self.ref(v)]
        try:
            r = repr(v)
        except Exception:
            r = "?"
        return ["X", r[:MAX_STR]]

    def heap_entry(self, obj, pending):
        e = lambda x: self.enc(x, pending)
        cls = type(obj).__name__
        if isinstance(obj, deque):
            items = list(itertools.islice(obj, MAX_ITEMS))
            return {"t": "deque", "c": cls, "items": [e(x) for x in items], "n": len(obj)}
        if isinstance(obj, (list, tuple)):
            return {"t": "list" if isinstance(obj, list) else "tuple", "c": cls,
                    "items": [e(x) for x in obj[:MAX_ITEMS]], "n": len(obj)}
        if isinstance(obj, (set, frozenset)):
            try:
                items = sorted(obj)
            except Exception:
                items = list(obj)
            return {"t": "set", "c": cls, "items": [e(x) for x in items[:MAX_ITEMS]], "n": len(obj)}
        if isinstance(obj, dict):
            ents = list(itertools.islice(obj.items(), MAX_ITEMS))
            return {"t": "dict", "c": cls, "entries": [[e(k), e(v)] for k, v in ents], "n": len(obj)}
        attrs = {}
        try:
            d = dict(vars(obj))
        except TypeError:
            d = {s: getattr(obj, s) for s in getattr(obj, "__slots__", ()) if hasattr(obj, s)}
        if "next" in d and "val" in d:
            return {"t": "lnode", "c": cls, "val": e(d["val"]), "next": e(d["next"]),
                    "extra": {k: e(v) for k, v in d.items() if k not in ("val", "next")}}
        if ("left" in d or "right" in d) and "val" in d:
            return {"t": "tnode", "c": cls, "val": e(d["val"]), "left": e(d.get("left")),
                    "right": e(d.get("right")),
                    "extra": {k: e(v) for k, v in d.items() if k not in ("val", "left", "right")}}
        for k, v in list(d.items())[:MAX_ITEMS]:
            if not k.startswith("__"):
                attrs[k] = e(v)
        return {"t": "obj", "c": cls, "attrs": attrs}

    def frame_vars(self, frame, pending, is_module):
        out = []
        items = frame.f_globals.items() if is_module else frame.f_locals.items()
        for name, v in items:
            if name.startswith("__"):
                continue
            if is_module:
                if name in HELPERS and HELPERS[name] is v:
                    continue
                if isinstance(v, (types.ModuleType, types.FunctionType, type)):
                    continue
            out.append([name, self.enc(v, pending)])
        return out

    def snapshot(self, frame, event, arg):
        frames = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == USER_FILE and f.f_code.co_name not in SKIP_FRAMES:
                frames.append(f)
            f = f.f_back
        frames.reverse()
        pending = []
        stack = []
        for fr in frames:
            is_module = fr.f_code.co_name == "<module>"
            stack.append({
                "fn": "globale" if is_module else fr.f_code.co_name,
                "line": fr.f_lineno,
                "vars": self.frame_vars(fr, pending, is_module),
                "fid": self.fids.get(id(fr), (0,))[0],
            })
        heap = {}
        while pending and len(heap) < MAX_HEAP:
            obj = pending.pop()
            hid = self.ids[id(obj)]
            if hid in heap:
                continue
            heap[hid] = self.heap_entry(obj, pending)
        step = {"line": frame.f_lineno, "ev": event, "stack": stack, "heap": heap,
                "out": len(self.out.getvalue())}
        if event == "return":
            step["ret"] = self.enc(arg, pending)
            while pending and len(heap) < MAX_HEAP:
                obj = pending.pop()
                hid = self.ids[id(obj)]
                if hid not in heap:
                    heap[hid] = self.heap_entry(obj, pending)
        self.steps.append(step)

    # ---------- trace ----------
    def tracer(self, frame, event, arg):
        if frame.f_code.co_filename != USER_FILE or frame.f_code.co_name in SKIP_FRAMES:
            return None
        self.calls += 1
        self.fids[id(frame)] = (self.calls, frame)
        frame.f_trace_opcodes = True
        return self.local

    def local(self, frame, event, arg):
        if self.stopped:
            raise StepLimit()
        if event == "opcode":
            # rete di sicurezza per cicli senza eventi "line" (es. `while True: pass`)
            self.ops += 1
            if self.ops % 20000 == 0 and time.time() - self.t0 > self.max_seconds:
                self.stopped = True
                raise StepLimit()
            return self.local
        if event in ("line", "return"):
            if len(self.steps) >= self.max_steps:
                self.stopped = True
                raise StepLimit()
            self.snapshot(frame, event, arg)
            if event == "return":
                self.fids.pop(id(frame), None)
        return self.local


def run_trace(code, max_steps=2000):
    rec = Recorder(int(max_steps))
    result = {"steps": rec.steps, "error": None, "limit": False, "errline": None}
    try:
        compiled = compile(code, USER_FILE, "exec")
    except SyntaxError as ex:
        result["error"] = f"SyntaxError: {ex.msg} (riga {ex.lineno})"
        result["errline"] = ex.lineno
        result["output"] = ""
        return json.dumps(result)
    g = {"__name__": "__main__", "__builtins__": __builtins__}
    g.update(HELPERS)
    old_out = sys.stdout
    sys.stdout = rec.out
    sys.settrace(rec.tracer)
    try:
        exec(compiled, g)
    except StepLimit:
        result["limit"] = True
    except RecursionError:
        result["error"] = "RecursionError: ricorsione troppo profonda"
    except Exception as ex:
        if rec.stopped:
            result["limit"] = True
        else:
            tb = ex.__traceback__
            line = None
            while tb is not None:
                if tb.tb_frame.f_code.co_filename == USER_FILE:
                    line = tb.tb_lineno
                tb = tb.tb_next
            result["error"] = f"{type(ex).__name__}: {ex}"
            result["errline"] = line
    finally:
        sys.settrace(None)
        sys.stdout = old_out
    result["output"] = rec.out.getvalue()
    return json.dumps(result)
