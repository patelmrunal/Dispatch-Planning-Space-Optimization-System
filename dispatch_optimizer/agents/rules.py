"""
rules.py
Rule-based filtering engine for warehouse storage constraints (fragility, weight, priority, etc.).
"""

def apply_rules(products, constraints):
    """
    Apply rule-based filters to the product list based on storage constraints.
    Args:
        products (list of dict): List of product data.
        constraints (dict): Constraints for filtering.
    Returns:
        list of dict: Filtered product list.
    """
    # Filter by max storage weight (cumulative)
    max_weight = constraints.get('max_storage_weight', float('inf'))
    filtered = []
    total_weight = 0
    for p in products:
        if total_weight + p['Weight'] <= max_weight:
            filtered.append(p)
            total_weight += p['Weight']
    # Sort by priority if needed
    if constraints.get('priority_first', False):
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        filtered.sort(key=lambda x: priority_order.get(x.get('Priority', 'Medium'), 1))
    # Place fragile items on top if needed
    if constraints.get('fragile_on_top', False):
        filtered.sort(key=lambda x: not x.get('Fragile', False))  # Fragile=True first
    return filtered 