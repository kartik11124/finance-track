"""Searching algorithms implemented from scratch.
Includes Linear Search, Binary Search, and Hash Indexing (Hash Map).
Time and space complexity documented for viva / 3rd-sem academic evaluation.
"""

from typing import Any, Callable, Dict, List, Optional


def linear_search(
    items: List[Dict[str, Any]],
    key: str,
    target: Any,
    match_partial: bool = False
) -> List[Dict[str, Any]]:
    """Linear Search: Searches through an unsorted list item by item.
    Time Complexity: O(n)
    Space Complexity: O(1) auxiliary
    """
    matches = []
    target_str = str(target).lower() if match_partial else target

    for item in items:
        val = item.get(key)
        if val is None:
            continue
        if match_partial:
            if target_str in str(val).lower():
                matches.append(item)
        else:
            if val == target:
                matches.append(item)
    return matches


def binary_search(
    sorted_items: List[Dict[str, Any]],
    key: str,
    target_val: float
) -> Optional[int]:
    """Binary Search: Searches for an exact match in a list sorted by `key`.
    Returns index of item if found, else None.
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    low = 0
    high = len(sorted_items) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_val = sorted_items[mid].get(key, 0)

        if mid_val == target_val:
            return mid
        elif mid_val < target_val:
            low = mid + 1
        else:
            high = mid - 1

    return None


def build_hash_index(
    items: List[Dict[str, Any]],
    index_key: str
) -> Dict[Any, List[Dict[str, Any]]]:
    """Hash Map Indexing: Groups items by `index_key` into a hash table (Python dictionary).
    Enables O(1) average-time lookups by category, risk level, etc.
    Time Complexity to build: O(n)
    Lookup Time Complexity: O(1) average
    Space Complexity: O(n)
    """
    hash_map: Dict[Any, List[Dict[str, Any]]] = {}
    for item in items:
        val = item.get(index_key)
        if val not in hash_map:
            hash_map[val] = []
        hash_map[val].append(item)
    return hash_map


def search_investments(
    investments: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """Multi-attribute search across investment name, category, and description."""
    if not query or not query.strip():
        return investments

    q = query.strip().lower()
    results = []
    for inv in investments:
        name = str(inv.get("name", "")).lower()
        cat = str(inv.get("category", "")).lower()
        desc = str(inv.get("description", "")).lower()
        goal = str(inv.get("suitable_goal", "")).lower()

        if q in name or q in cat or q in desc or q in goal:
            results.append(inv)
    return results
