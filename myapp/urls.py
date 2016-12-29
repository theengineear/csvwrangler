from django.conf.urls import url

from external_data.views import CsvUpload

# This is mostly for example, this wouldn't really be top-level.
# Typically some documented api root would be top-level for this app.
urlpatterns = [
    url(r'', CsvUpload.as_view(), name='csv-upload'),
]
