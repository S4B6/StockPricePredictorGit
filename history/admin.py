from django.contrib import admin
from .models import HistoryPage 
from .models import HistoryChart 

@admin.register(HistoryPage)
class HistoryPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "asset_class", "category", "subcategory", "last_update")
    search_fields = ("title", "slug", "asset_class", "category", "subcategory")
    list_filter = ("asset_class", "category")
    
    # turn OFF Django automatic slug creation
    prepopulated_fields = {}

    # help text so you always write the correct slug
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

@admin.register(HistoryChart)
class HistoryChartAdmin(admin.ModelAdmin):
    list_display = ("page", "title", "chart_type", "order")
    list_filter = ("chart_type", "page")
    search_fields = ("title", "page__slug")
    ordering = ("page", "order")