import six
from django.db.models import Case, When, Q, F, Sum, CharField, Value
from django.db.models.functions import Coalesce
from django.shortcuts import _get_queryset

from django_pivot.utils import get_column_values, get_field_choices, default_fill


def pivot(queryset, rows, column, data, aggregation=Sum, choices='auto', display_transform=lambda s: s, default=None, row_range=()):
    """
    Takes a queryset and pivots it. The result is a table with one record
    per unique value in the `row` column, a column for each unique value in the `column` column
    and values in the table aggregated by the data column.

    :param queryset: a QuerySet, Model, or Manager
    :param rows: list of strings, name of columns that will key the rows
    :param column: string, name of column that will define columns
    :param data: column name or Combinable
    :param aggregation: aggregation function to apply to data column
    :param display_transform: function that takes a string and returns a string
    :param default: default value to pass to the aggregate function when no record is found
    :param row_range: iterable with the expected range of rows in the result
    :return: ValuesQueryset
    """
    values = [rows] if isinstance(rows, six.string_types) else list(rows)

    queryset = _get_queryset(queryset)

    column_values = get_column_values(queryset, column, choices)

    annotations = _get_annotations(column, column_values, data, aggregation, display_transform, default=default)
    for row in values:
        row_choices = get_field_choices(queryset, row)
        if row_choices:
            whens = (When(Q(**{row: value}), then=Value(display_value, output_field=CharField())) for value, display_value in row_choices)
            row_display = Case(*whens)
            queryset = queryset.annotate(**{'get_' + row + '_display': row_display})
            values.append('get_' + row + '_display')

    values_list = queryset.values(*values).annotate(**annotations)

    if row_range:
        attributes = [value[0] for value in column_values]
        values_list = default_fill(values_list, values[0], row_range, fill_value=default, fill_attributes=attributes)

    return values_list


def _get_annotations(column, column_values, data, aggregation, display_transform=lambda s: s, default=None):
    value = data if hasattr(data, 'resolve_expression') else F(data)
    return {
        display_transform(display_value): Coalesce(aggregation(Case(When(Q(**{column: column_value}), then=value))), default)
        for column_value, display_value in column_values
    }
