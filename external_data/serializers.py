from rest_framework import serializers


class CsvUploadSerializer(serializers.Serializer):
    """This exists to easily populate browseable api forms in DRF."""
    group = serializers.CharField(max_length=200)
    aggregate = serializers.CharField(max_length=200)
    file = serializers.FileField()
