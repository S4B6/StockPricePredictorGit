from django.contrib import admin
from django.http import HttpResponse
import json

from .models import HistoryPage, HistoryChart


# ============================
# Custom Export Action
# ============================
def export_history_pages_json(modeladmin, request, queryset):
    data = []

    for obj in queryset:
        data.append({
            "title": obj.title,
            "slug": obj.slug,
            "asset_class": obj.asset_class,
            "category": obj.category,
            "subcategory": obj.subcategory,
            "content": obj.content,
            "last_update": obj.last_update.isoformat() if obj.last_update else None,
        })

    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json"
    )
    response['Content-Disposition'] = 'attachment; filename="history_pages_backup.json"'
    return response

export_history_pages_json.short_description = "Export selected pages as JSON"


# ============================
# Admin Panels
# ============================
@admin.register(HistoryPage)
class HistoryPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "asset_class", "category", "subcategory", "last_update")
    search_fields = ("title", "slug", "asset_class", "category", "subcategory")
    list_filter = ("asset_class", "category")

    # Add export action here
    actions = [export_history_pages_json]

    prepopulated_fields = {}  # Prevent Django from auto-filling slugs
    readonly_fields = ()

    fieldsets = (
        (None, {
            "fields": (
                "title",
                "slug",
                "asset_class",
                "category",
                "subcategory",
                "content",
            ),
            "description": (
                "<b>Slug format must follow:</b><br>"
                "rates/policy-rates/ecb<br>"
                "macro/growth/us<br>"
                "equity/by-geography/europe<br>"
                "commodities/energy/oil<br>"
                "<br>"
                "<i>No spaces, only lowercase, use hyphens inside words.</i>"
            ),
        }),
    )

# ============================
# Export HistoryCharts as JSON
# ============================
def export_history_charts_json(modeladmin, request, queryset):
    data = []

    for chart in queryset:
        data.append({
            "page_title": chart.page.title if chart.page else None,
            "page_slug": chart.page.slug if chart.page else None,
            "title": chart.title,
            "chart_type": chart.chart_type,
            "order": chart.order,
            "sql_query": chart.sql_query,
            "show_download": chart.show_download,
        })

    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json"
    )
    response['Content-Disposition'] = 'attachment; filename="history_charts_backup.json"'
    return response

export_history_charts_json.short_description = "Export selected charts as JSON"

@admin.register(HistoryChart)
class HistoryChartAdmin(admin.ModelAdmin):
    list_display = ("page", "title", "chart_type", "order")
    list_filter = ("chart_type", "page")
    search_fields = ("title", "page__slug")
    ordering = ("page", "order")

    actions = [export_history_charts_json]  # ← Add this line



