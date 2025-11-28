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

    chart_type = models.CharField(
        max_length=30,
        choices=[
            ("line", "Line Chart"),
            ("area", "Area Chart"),
            ("bar", "Bar Chart"),
            ("heatmap_mm", "Money Market Heatmap"),
            ("line_regime", "Line with Regime Shading"),
            ("mad_hybrid", "Money Market MAD"),
        ],
        default="line"
    )

    order = models.PositiveIntegerField(default=1)

    show_download = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.page.slug} — {self.title}"