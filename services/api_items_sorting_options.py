from datetime import datetime

def to_comparable(val):
    """
    Convert ISO datetime strings to datetime objects for proper sorting.
    Fallback to original value for non-date types.
    """
    if isinstance(val, str) and 'T' in val:
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            return val
    return val

def partition_asc(items, start, end, option):
    pivot_item = items[end]
    pointer1 = start - 1
    pointer2 = start

    while pointer2 < end:
        val2 = to_comparable(items[pointer2].get(option))
        pivot_val = to_comparable(pivot_item.get(option))

        if val2 is not None and pivot_val is not None and val2 < pivot_val:
            pointer1 += 1
            items[pointer1], items[pointer2] = items[pointer2], items[pointer1]
        pointer2 += 1

    items[pointer1 + 1], items[end] = items[end], items[pointer1 + 1]
    return pointer1 + 1

def partition_desc(items, start, end, option):
    pivot_item = items[end]
    pointer1 = start - 1
    pointer2 = start

    while pointer2 < end:
        val2 = to_comparable(items[pointer2].get(option))
        pivot_val = to_comparable(pivot_item.get(option))

        if val2 is not None and pivot_val is not None and val2 > pivot_val:
            pointer1 += 1
            items[pointer1], items[pointer2] = items[pointer2], items[pointer1]
        pointer2 += 1

    items[pointer1 + 1], items[end] = items[end], items[pointer1 + 1]
    return pointer1 + 1

def sort_items_list(items, start_index, end_index, option, order_by):
    if start_index >= end_index:
        return

    if order_by == 'ascending':
        pivot_index = partition_asc(items, start_index, end_index, option)
        sort_items_list(items, start_index, pivot_index - 1, option, order_by)
        sort_items_list(items, pivot_index + 1, end_index, option, order_by)
    else:
        pivot_index = partition_desc(items, start_index, end_index, option)
        sort_items_list(items, start_index, pivot_index - 1, option, order_by)
        sort_items_list(items, pivot_index + 1, end_index, option, order_by)
