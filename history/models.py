from django.db import models

class HistoryPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # e.g. "rates/policy-rates/fed"

    asset_class = models.CharField(max_length=50)      # "rates"
    category = models.CharField(max_length=100)        # "Policy Rates"
    subcategory = models.CharField(max_length=100)     # "Fed"

    content = models.TextField(blank=True)             # free-form HTML
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
