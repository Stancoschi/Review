"""Basic data structures, each used on a small practical problem.

Run:  python structures.py
"""

from collections import deque


# ---- Stack (list, last in first out) ----
def brackets_ok(text):
    """Are (), [] and {} closed in the right order? Useful for config lines."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
    return not stack


# ---- Binary search tree (sorted keys; insert, search, delete, traversal) ----
class Node:
    def __init__(self, key, value):
        self.key, self.value = key, value
        self.left = self.right = None


def insert(node, key, value):
    if node is None:
        return Node(key, value)
    if key < node.key:
        node.left = insert(node.left, key, value)
    elif key > node.key:
        node.right = insert(node.right, key, value)
    else:
        node.value = value
    return node


def search(node, key):
    while node and node.key != key:
        node = node.left if key < node.key else node.right
    return node.value if node else None


def delete(node, key):
    if node is None:
        return None
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        node.right = delete(node.right, key)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        smallest = node.right                    # replace with next bigger key
        while smallest.left:
            smallest = smallest.left
        node.key, node.value = smallest.key, smallest.value
        node.right = delete(node.right, smallest.key)
    return node


def in_order(node):
    return in_order(node.left) + [(node.key, node.value)] + in_order(node.right) \
        if node else []


# ---- Sorted list + binary search ----
def binary_search(items, target):
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        low, high = (mid + 1, high) if items[mid] < target else (low, mid - 1)
    return -1


if __name__ == "__main__":
    print("1) Stack: are the brackets of a config line valid?")
    for text in ['{"hosts": ["a", "b"]}', '{"hosts": ["a", "b"}']:
        print(f"   {text:<24} {brackets_ok(text)}")

    print("\n2) Queue (deque): failed jobs are retried in the order they failed")
    retry = deque(["load_sales", "load_orders", "load_customers"])
    retry.append("load_payments")               # a new failure joins the back
    while retry:
        print("   retrying", retry.popleft())

    print("\n3) Hash table (dict): errors per service")
    errors = {}
    for service in ["api", "db", "api", "db", "db", "etl"]:
        errors[service] = errors.get(service, 0) + 1
    print("  ", errors, "| db:", errors["db"])

    print("\n4) Binary search tree: file sizes in MB, kept sorted")
    root = None
    for name, size in [("a.csv", 120), ("b.csv", 15), ("c.csv", 300), ("d.csv", 45)]:
        root = insert(root, size, name)
    print("   in order:", in_order(root))
    print("   search 45:", search(root, 45), "| search 99:", search(root, 99))
    root = delete(root, 120)
    print("   after deleting 120:", in_order(root))

    print("\n5) Array (list) + binary search: hours with errors")
    hours = [8, 9, 10, 11, 14, 17]
    print("   10 ->", binary_search(hours, 10), "| 12 ->", binary_search(hours, 12))
