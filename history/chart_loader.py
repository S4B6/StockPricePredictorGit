import importlib
from functools import lru_cache

@lru_cache(maxsize=100)
def load_chart_renderer(chart_type):
    """
    Convert chart_type like:
        'rates.policy_rates.mm_bubble_map'
    into module path:
        history.charts.rates.policy_rates.mm_bubble_map
    Then import & return the 'render(df, title)' function.
    """

    module_path = f"history.charts.{chart_type}"

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise ImportError(
            f"[Chart ERROR] Module not found for chart_type '{chart_type}'. "
            f"Looked for: {module_path}"
        ) from e

    if not hasattr(module, "render"):
        raise AttributeError(
            f"[Chart ERROR] Module '{module_path}' must define a function: render(df, title)"
        )

    return module.render
