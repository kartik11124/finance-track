"""Sorting algorithms implemented from scratch for academic evaluation.
Includes QuickSort and MergeSort with configurable key extractors.
Time and space complexity documented for viva demonstration.
"""

from typing import Any, Callable, Dict, List, Union


def _extract_val(item: Any, key: Union[str, Callable[[Any], Any]]) -> Any:
    """Helper to extract sortable value from dictionary or object."""
    if callable(key):
        return key(item)
    if isinstance(item, dict):
        return item.get(key, 0)
    return getattr(item, key, 0)


def quicksort(
    items: List[Any],
    key: Union[str, Callable[[Any], Any]],
    reverse: bool = False
) -> List[Any]:
    """QuickSort algorithm: Divide-and-conquer based on pivot partitioning.
    Time Complexity:
      - Average case: O(n log n)
      - Best case: O(n log n)
      - Worst case: O(n^2) (rare with middle pivot)
    Space Complexity: O(log n) call stack
    """
    if len(items) <= 1:
        return list(items)

    arr = list(items)
    pivot = _extract_val(arr[len(arr) // 2], key)

    if not reverse:
        left = [x for x in arr if _extract_val(x, key) < pivot]
        middle = [x for x in arr if _extract_val(x, key) == pivot]
        right = [x for x in arr if _extract_val(x, key) > pivot]
        return quicksort(left, key, reverse) + middle + quicksort(right, key, reverse)
    else:
        left = [x for x in arr if _extract_val(x, key) > pivot]
        middle = [x for x in arr if _extract_val(x, key) == pivot]
        right = [x for x in arr if _extract_val(x, key) < pivot]
        return quicksort(left, key, reverse) + middle + quicksort(right, key, reverse)


def mergesort(
    items: List[Any],
    key: Union[str, Callable[[Any], Any]],
    reverse: bool = False
) -> List[Any]:
    """MergeSort algorithm: Stable divide-and-conquer sorting.
    Time Complexity: O(n log n) in all cases (Worst, Average, Best)
    Space Complexity: O(n) auxiliary space
    """
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left = mergesort(items[:mid], key, reverse=reverse)
    right = mergesort(items[mid:], key, reverse=reverse)

    return _merge(left, right, key, reverse=reverse)


def _merge(
    left: List[Any],
    right: List[Any],
    key: Union[str, Callable[[Any], Any]],
    reverse: bool
) -> List[Any]:
    """Merge step of MergeSort."""
    merged = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        v1 = _extract_val(left[i], key)
        v2 = _extract_val(right[j], key)

        condition = (v1 >= v2) if reverse else (v1 <= v2)
        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def sort_investments(
    investments: List[Dict[str, Any]],
    sort_by: str = "score",
    reverse: bool = True
) -> List[Dict[str, Any]]:
    """Convenience helper using QuickSort to sort investments by specific fields."""
    valid_keys = {
        "score": "score",
        "minimum_amount": "minimum_amount",
        "expected_return": "expected_return_rate",
        "name": "name"
    }
    target_key = valid_keys.get(sort_by, "score")
    # For minimum_amount default ascending unless specified
    if sort_by == "minimum_amount":
        reverse = not reverse
    return quicksort(investments, key=target_key, reverse=reverse)
