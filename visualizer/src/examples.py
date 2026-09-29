# Esempi precaricati nel visualizzatore. build.py li inserisce nella pagina.
EXAMPLES = [
    ("Invertire una linked list", "Linked list", '''class Solution:
    def reverseList(self, head):
        prev, cur = None, head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        return prev


head = build_list([1, 2, 3, 4, 5])
nuova = Solution().reverseList(head)
print(list_to_array(nuova))
'''),
    ("Two Sum", "Hash map", '''class Solution:
    def twoSum(self, nums, target):
        visti = {}
        for i, x in enumerate(nums):
            manca = target - x
            if manca in visti:
                return [visti[manca], i]
            visti[x] = i
        return []


print(Solution().twoSum([3, 8, 11, 2, 7, 15], 9))
'''),
    ("Ricerca binaria", "Array", '''class Solution:
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


print(Solution().search([-4, -1, 0, 3, 5, 9, 12, 17, 21], 12))
'''),
    ("Sottostringa senza ripetizioni", "Sliding window", '''class Solution:
    def lengthOfLongestSubstring(self, s):
        ultimo = {}
        left = 0
        best = 0
        for right, ch in enumerate(s):
            if ch in ultimo and ultimo[ch] >= left:
                left = ultimo[ch] + 1
            ultimo[ch] = right
            best = max(best, right - left + 1)
        return best


print(Solution().lengthOfLongestSubstring("abcabcbb"))
'''),
    ("Ciclo in una lista (Floyd)", "Linked list", '''class Solution:
    def hasCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False


head = build_list([3, 2, 0, -4, 7])
coda = head.next.next.next.next
coda.next = head.next          # crea il ciclo
print(Solution().hasCycle(head))
'''),
    ("Unire due liste ordinate", "Linked list", '''class Solution:
    def mergeTwoLists(self, l1, l2):
        dummy = tail = ListNode(0)
        while l1 and l2:
            if l1.val <= l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next
        tail.next = l1 or l2
        return dummy.next


a = build_list([1, 2, 4])
b = build_list([1, 3, 4])
print(list_to_array(Solution().mergeTwoLists(a, b)))
'''),
    ("Profondità di un albero", "Ricorsione", '''class Solution:
    def maxDepth(self, root):
        if root is None:
            return 0
        sx = self.maxDepth(root.left)
        dx = self.maxDepth(root.right)
        return 1 + max(sx, dx)


root = build_tree([3, 9, 20, None, None, 15, 7])
print(Solution().maxDepth(root))
'''),
    ("Inserire in un BST", "Albero", '''def inserisci(root, val):
    if root is None:
        return TreeNode(val)
    node = root
    while True:
        if val < node.val:
            if node.left is None:
                node.left = TreeNode(val)
                break
            node = node.left
        else:
            if node.right is None:
                node.right = TreeNode(val)
                break
            node = node.right
    return root


root = None
for v in [50, 30, 70, 20, 40, 60, 80, 35]:
    root = inserisci(root, v)
'''),
    ("Visita per livelli (BFS)", "Albero + coda", '''class Solution:
    def levelOrder(self, root):
        livelli = []
        q = deque([root])
        while q:
            livello = []
            for _ in range(len(q)):
                node = q.popleft()
                livello.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            livelli.append(livello)
        return livelli


print(Solution().levelOrder(build_tree([1, 2, 3, 4, 5, None, 6])))
'''),
    ("BFS su un grafo", "Grafo", '''def bfs(graph, start):
    visited = {start}
    q = deque([start])
    ordine = []
    while q:
        node = q.popleft()
        ordine.append(node)
        for nei in graph[node]:
            if nei not in visited:
                visited.add(nei)
                q.append(nei)
    return ordine


graph = {
    "A": ["B", "C"],
    "B": ["A", "D", "E"],
    "C": ["A", "F"],
    "D": ["B"],
    "E": ["B", "F"],
    "F": ["C", "E"],
}
print(bfs(graph, "A"))
'''),
    ("DFS ricorsiva su un grafo", "Grafo", '''def dfs(adj, node, visited, ordine):
    visited.add(node)
    ordine.append(node)
    for nei in adj[node]:
        if nei not in visited:
            dfs(adj, nei, visited, ordine)


adj = {0: [1, 2], 1: [0, 3], 2: [0, 3, 4], 3: [1, 2, 5], 4: [2], 5: [3]}
ordine = []
dfs(adj, 0, set(), ordine)
print(ordine)
'''),
    ("Numero di isole", "Matrice + BFS", '''class Solution:
    def numIslands(self, grid):
        rows, cols = len(grid), len(grid[0])
        isole = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "1":
                    isole += 1
                    q = deque([(r, c)])
                    grid[r][c] = "0"
                    while q:
                        i, j = q.popleft()
                        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == "1":
                                grid[ni][nj] = "0"
                                q.append((ni, nj))
        return isole


grid = [
    ["1", "1", "0", "0", "0"],
    ["1", "1", "0", "1", "0"],
    ["0", "0", "1", "0", "0"],
    ["0", "0", "0", "1", "1"],
]
print(Solution().numIslands(grid))
'''),
    ("Coin change", "Programmazione dinamica", '''class Solution:
    def coinChange(self, coins, amount):
        dp = [0] + [inf] * amount
        for a in range(1, amount + 1):
            for c in coins:
                if c <= a and dp[a - c] + 1 < dp[a]:
                    dp[a] = dp[a - c] + 1
        return dp[amount] if dp[amount] != inf else -1


print(Solution().coinChange([1, 3, 4], 6))
'''),
    ("K-esimo più grande (heap)", "Heap", '''class Solution:
    def findKthLargest(self, nums, k):
        heap = []
        for x in nums:
            heapq.heappush(heap, x)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0]


print(Solution().findKthLargest([3, 2, 1, 5, 6, 4, 8, 7], 3))
'''),
    ("Parentesi valide", "Stack", '''class Solution:
    def isValid(self, s):
        coppie = {")": "(", "]": "[", "}": "{"}
        stack = []
        for ch in s:
            if ch in coppie:
                if not stack or stack[-1] != coppie[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)
        return not stack


print(Solution().isValid("{[()()]}"))
'''),
    ("Insertion sort", "Ordinamento", '''def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


print(insertion_sort([5, 2, 9, 1, 5, 6]))
'''),
    ("Merge sort", "Divide et impera", '''def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
'''),
]
