import csv
from collections import defaultdict

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException, MethodNotAllowed

from external_data.serializers import CsvUploadSerializer


class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST


class CsvUpload(CreateAPIView):
    """
    Csv Uploader Endpoint

    This endpoint allows users to upload a csv file with some post params to
    group and aggregate the data in the file.

    ### Quickstart

    The easiest way to start playing around is to use the rest framework's
    browseable api to make post requests.

    Use the `HTML form` tab in the bottom right to get going.

    ### Programmatic access

    If you're ready to access the api outside of the DRF interface, you can do
    something like:

        curl -X POST -F 'group=last_name' -F 'aggregate=count' -F 'file=@file0.csv' http://127.0.0.1:8000

    Where:

        * "http://127.0.0.1:8000" would be the url for application server.
        * "file0.csv" would be is the relative path to the file to upload.
        * "last_name" would be the column name to *group* on.
        * "count" would be the column name to *aggregate* by.

    More generically:

        curl -X POST -F 'group=<group>' -F 'aggregate=<aggregate>' -F 'file=@<file-path>' <url>

    ### Errors

    Bad (but anticipated) requests will return with a 400 Bad Request status
    and will contain a resulting `detail` field explaining what went wrong.

    """
    serializer_class = CsvUploadSerializer

    def get_queryset(self):
        """Just here to keep DRF happy."""
        return None

    def create(self, request, *args, **kwargs):

        aggregate = request.data.get('aggregate')
        group = request.data.get('group')
        if not aggregate or not group:
            raise BadRequestException(
                detail='Aggregate and group must be defined.')

        f = request.data.get('file')
        if not f or not isinstance(f, InMemoryUploadedFile):
            raise BadRequestException(detail='File must be file-like.')

        csv_f = csv.reader(f)
        aggregate_index = None
        group_index = None
        header_found = False
        results = defaultdict(int)
        for row in csv_f:
            if not [c for c in row if c]:
                # The row is empty, e.g., ['', '', '']
                continue

            if not header_found:
                # We found the first non-empty row. Get computation indices.
                header_found = True
                try:
                    aggregate_index = row.index(aggregate)
                    group_index = row.index(group)
                except ValueError:
                    detail = (
                        'Group and aggregate must be in headers. Headers: {}'
                        .format(row)
                    )
                    raise BadRequestException(detail=detail)

            # Ok, we're iterating through the body of the csv (non-headers).
            group_value = row[group_index]
            try:
                aggregate_value = int(row[aggregate_index])
            except ValueError:
                aggregate_value = None

            if not group_value or aggregate_value is None:
                # Don't make guesses on what to do here, just ignore.
                # It'd be too annoying to flake for this case, so we do our
                # best and try the next row.
                continue

            results[group_value] += aggregate_value

        return Response(data=dict(results))

    def list(self, request, pk=None):
        """Simply here to ensure documentation shows for this view."""
        raise MethodNotAllowed('GET')
