from django.contrib import admin
from .models import HistoryPage

@admin.register(HistoryPage)
class HistoryPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "asset_class", "category", "subcategory", "last_update")
    search_fields = ("title", "slug", "asset_class", "category", "subcategory")
    list_filter = ("asset_class", "category")
    prepopulated_fields = {"slug": ("title",)}