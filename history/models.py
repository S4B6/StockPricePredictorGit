# history/models.py

from django.db import models

class HistoryPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=300, unique=True)

    asset_class = models.CharField(max_length=50)      # "rates"
    category = models.CharField(max_length=100)        # "Policy Rates"
    subcategory = models.CharField(max_length=100)     # "Fed"

    content = models.TextField(blank=True)             # free-form HTML
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# -----------------------------------------------------
# UPDATED HistoryChart WITH NEW MODULAR chart_type
# -----------------------------------------------------
class HistoryChart(models.Model):
    page = models.ForeignKey(
        HistoryPage,
        on_delete=models.CASCADE,
        related_name="charts"
    )

    title = models.CharField(max_length=200)

    sql_query = models.TextField(
        help_text="SQL query returning at least: date, value columns"
    )

    # -------------------------------------------------
    # NEW CHART TYPE CHOICES — CLEAN + MODULAR
    # -------------------------------------------------
    CHART_TYPES = [

        # -------------------------------
        # Generic charts
        # -------------------------------
        ("generic.line_generic", "Generic Line Chart"),
        ("generic.line_regime", "Generic Line Chart with Regime Shading"),

        # -------------------------------
        # Rates → Policy Rates → Money Markets
        # -------------------------------
        ("rates.policy_rates.mm_bubble_map", "MM Bubble Map"),
        ("rates.policy_rates.mm_heatmap", "MM Heatmap"),
        ("rates.policy_rates.mm_line_mad_hybrid", "MM MAD Hybrid Line"),
        ("rates.policy_rates.mm_line_ma_regime", "MM MA5 Regime Line"),
    ]
    chart_type = models.CharField(
        max_length=40,
        choices=CHART_TYPES,
        default="line"
    )

    order = models.PositiveIntegerField(default=1)

    show_download = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.page.slug} — {self.title}"
