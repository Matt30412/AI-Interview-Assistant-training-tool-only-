# AI Interview Assistant (training tool only)

A set of tools for practising coding interviews. The first tool is **Moviola SDA**, a step-by-step
visualizer for LeetCode-style problems: you write a solution in Python and watch the data move
through your data structures, one line at a time, like a video.

> *Moviola* is the Italian word for a slow-motion replay; *SDA* stands for *Strutture Dati e
> Algoritmi* (Data Structures and Algorithms). The interface is in Italian.

## Contents

- [Features](#features)
- [Quick start](#quick-start)
- [Writing code for the visualizer](#writing-code-for-the-visualizer)
- [Controls](#controls)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Development](#development)
- [Limitations](#limitations)
- [Third-party software](#third-party-software)
- [License](#license)

## Features

- **Animated playback.** Nodes slide to their new positions, pointers move between cells and
  arrows re-target smoothly between steps. Play, pause and adjust the speed from 1 to 30 steps
  per second.
- **Timeline scrubber.** The timeline plots the call-stack depth over the whole run, so recursion
  shows up as a mountain range. Click or drag to jump to any step.
- **Data structures, drawn the way you draw them on paper:**

  | Structure | How it is shown |
  | --- | --- |
  | Arrays and strings | Cells with indices; integer variables such as `i`, `j`, `lo`, `mid`, `hi`, `left`, `right` become coloured pointers under the cells, and a `left`/`right` pair highlights the window between them |
  | Linked lists | Boxes with `next` arrows; reversals, merges and cycles (Floyd) are visible as arrows changing direction |
  | Binary trees | In-order layout; nodes still on the recursion stack are tinted, the current node is outlined |
  | Graphs | From an adjacency `dict` or list; force-directed layout with visited and queued nodes coloured and `node`/`nei` labels moving between nodes |
  | Matrices | Grids and 2D DP tables, with `(r, c)` pointer pairs, visited cells and "land" cells highlighted |
  | Hash maps and sets | Key/value tables and chips; new or changed entries flash |
  | Stacks, queues, heaps | Top/front/back markers; lists named `heap` are also drawn as a binary tree |
  | Call stack | Every active frame with its local variables and return values |

- **17 built-in examples**: reverse a linked list, Two Sum, binary search, longest substring
  without repeats (sliding window), Floyd's cycle detection, merge two sorted lists, tree depth,
  BST insertion, level-order traversal, BFS and DFS on graphs, number of islands, coin change,
  k-th largest with a heap, valid parentheses, insertion sort and merge sort.
- **Light and dark themes**, following the system setting. The layout adapts to phone screens.

## Quick start

1. Open `visualizer/index.html` in a modern browser (Chrome, Firefox, Safari or Edge).
2. Wait for the status indicator in the top-right corner to read **Python pronto**. The first
   load downloads the Python runtime ([Pyodide](https://pyodide.org)) from jsDelivr, so an
   internet connection is required.
3. Pick an example from the drop-down menu or write your own code.
4. Press **Esegui** (Run) or `Ctrl`+`Enter`.

No build step, server or installation is needed to use the tool.

## Writing code for the visualizer

Write normal Python, including the usual LeetCode `class Solution` wrapper, and call your
function at the bottom of the file:

```python
class Solution:
    def search(self, nums, target):
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                return mid
            if nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1


print(Solution().search([-4, -1, 0, 3, 5, 9, 12], 9))
```

These helpers are available without importing anything:

| Name | Purpose |
| --- | --- |
| `ListNode(val, next)` | Linked-list node, same shape as on LeetCode |
| `TreeNode(val, left, right)` | Binary-tree node, same shape as on LeetCode |
| `build_list([1, 2, 3])` | Builds a linked list and returns its head |
| `build_tree([3, 9, 20, None, None, 15, 7])` | Builds a tree from LeetCode's level-order notation |
| `list_to_array(head)` | Converts a linked list back to a Python list |
| `deque`, `defaultdict`, `Counter`, `OrderedDict` | From `collections` |
| `heapq`, `bisect`, `itertools`, `functools`, `math` | Standard modules |
| `List`, `Optional`, `Dict`, `Set`, `Tuple` | Type hints |
| `inf` | `math.inf` |

**How structures are recognised.** The visualizer infers what to draw from the shape of the data
and from variable names:

- An integer becomes a pointer on an array when you use it as an index of that array anywhere in
  the code (`nums[mid]`, `s[right]`), or when it has a typical index name (`i`, `j`, `left`,
  `right`, `lo`, `hi`, `mid`, `slow`, `fast`, …).
- A dict or list of lists is drawn as a graph when it is named `graph`, `adj`, `g` or similar, or
  when most of its values are lists of its own keys.
- Lists named `stack`, `queue`/`q` or `heap`/`pq` get stack, queue or heap markers.
- A rectangular list of lists of plain values is drawn as a matrix.
- Any object with `val` and `next` attributes is a linked-list node, and any object with `val`
  and `left`/`right` is a tree node, so your own node classes work too.

## Controls

| Action | Control |
| --- | --- |
| Run the code | **Esegui** button or `Ctrl`/`Cmd` + `Enter` |
| Play / pause | **Play** button or `Space` |
| Previous / next step | Arrow buttons or `←` / `→` |
| First / last step | Buttons or `Home` / `End` |
| Jump to any step | Click or drag on the timeline |
| Jump to the next execution of a line | Click the line number in the editor |
| Zoom | Mouse wheel or the `+` / `−` buttons |
| Pan | Drag the empty background |
| Move a structure | Drag it; graph nodes can be dragged one by one |
| Reset the camera | **Inquadra** (Fit) |
| Playback speed and step limit | **Velocità** and **Limite** menus |

## How it works

1. **Tracing.** Your code runs inside the browser in CPython compiled to WebAssembly (Pyodide).
   `visualizer/src/tracer.py` installs a `sys.settrace` hook and, before every executed line and
   at every function return, records the call stack and every object reachable from the local
   and global variables. Objects get stable ids, so the same list or node can be followed from
   one step to the next.
2. **Safety limits.** Execution stops after the chosen number of steps (1000, 3000 or 8000) or
   after about 8 seconds, so infinite loops, including `while True: pass`, cannot freeze the
   page. Syntax errors and runtime exceptions are reported with the line that caused them.
3. **Layout.** For each step the page turns the recorded state into a scene: every cell, node,
   pointer and arrow gets a stable key and a position. Linked-list nodes keep their slot across
   steps, graph positions are computed once with a force-directed layout, and sections are packed
   into columns to fit the viewport.
4. **Animation.** A small tweening engine interpolates positions, sizes and opacity between the
   previous scene and the new one, re-draws arrows along the moving endpoints and follows the
   content with the camera.

## Project structure

```
.
├── LICENSE
├── README.md
└── visualizer/
    ├── index.html          # generated, self-contained page: open this one
    ├── build.py            # assembles index.html from src/
    └── src/
        ├── template.html   # UI, scene layout and animation engine
        ├── tracer.py       # Python tracer that runs inside Pyodide
        ├── examples.py     # built-in examples
        └── codemirror.css  # CodeMirror 5 stylesheet, inlined into the page
```

## Development

Requirements: Python 3.10 or later. No third-party Python packages are needed.

Edit the files in `visualizer/src/`, then regenerate the page:

```sh
python3 visualizer/build.py
```

The build script inlines the tracer, the examples and the CodeMirror stylesheet into
`visualizer/index.html`. It also runs the first example with your local Python and embeds the
result, so the page can show an animation while Pyodide is still loading.

To serve the page locally instead of opening it from disk:

```sh
python3 -m http.server --directory visualizer 8000
# then open http://localhost:8000
```

If a `visualizer/pyodide/` folder containing the Pyodide distribution is present, the page loads
Python from there and does not need the CDN.

## Limitations

- Only Python is supported.
- The first run needs an internet connection to download Pyodide (about 13 MB, then cached by
  the browser).
- `input()` and file or network access are not available.
- Containers larger than 120 elements and scenes with more than 400 objects per step are
  truncated.
- Structure detection is heuristic. With unusual variable names a structure may be drawn as a
  plain list or table instead of a graph or a pointer.
- Execution is recorded first and replayed afterwards, so very long runs take a moment before
  playback starts.

## Third-party software

The page loads these libraries at runtime from public CDNs:

- [Pyodide](https://github.com/pyodide/pyodide) 0.26.4, Mozilla Public License 2.0
- [CodeMirror](https://codemirror.net/5/) 5.65.16, MIT License. Its stylesheet is included in
  `visualizer/src/codemirror.css`.
- Fonts from Google Fonts: Atkinson Hyperlegible, Bricolage Grotesque and JetBrains Mono, SIL
  Open Font License 1.1

## License

Released under the [MIT License](LICENSE).
