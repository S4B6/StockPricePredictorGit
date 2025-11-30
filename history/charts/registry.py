from ..chart_loader import load_chart_renderer
from .generic.line_generic import render as generic_line_render

REGISTRY = {
    # Old simple chart types (compatibility):
    "line": generic_line_render,
}

def get_chart_renderer(chart_type):
    """
    Chart routing:
    1. If chart_type is explicitly registered → return it
    2. If chart_type contains dots → treat as hierarchical module path
    3. Otherwise → fallback to generic or error
    """

    # 1) Explicit registered types first
    if chart_type in REGISTRY:
        return REGISTRY[chart_type]

    # 2) Hierarchical chart: rates.policy_rates.mm_factor_map
    if "." in chart_type:
        return load_chart_renderer(chart_type)

    # 3) Unknown → fallback or error
    raise ValueError(
        f"Unknown chart_type '{chart_type}'. "
        "If this is a specific chart, create a file "
        f"history/charts/{chart_type}.py or use dot notation."
    )
