import six
from django.db.models import Case, When, Q, F, Sum, CharField, Value
from django.shortcuts import _get_queryset

from django_pivot.utils import get_column_values, get_field_choices


def pivot(queryset, rows, column, data, aggregation=Sum, choices='auto', display_transform=lambda s: s):
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
    :return: ValuesQueryset
    """
    values = [rows] if isinstance(rows, six.string_types) else list(rows)

    queryset = _get_queryset(queryset)

    column_values = get_column_values(queryset, column, choices)

    annotations = _get_annotations(column, column_values, data, aggregation, display_transform)
    for row in values:
        row_choices = get_field_choices(queryset, row)
        if row_choices:
            whens = (When(Q(**{row: value}), then=Value(display_value, output_field=CharField())) for value, display_value in row_choices)
            row_display = Case(*whens)
            queryset = queryset.annotate(**{'get_' + row + '_display': row_display})
            values.append('get_' + row + '_display')

    return queryset.values(*values).annotate(**annotations)


def _get_annotations(column, column_values, data, aggregation, display_transform=lambda s: s):
    value = data if hasattr(data, 'resolve_expression') else F(data)
    return {
        display_transform(display_value): aggregation(Case(When(Q(**{column: column_value}), then=value)))
        for column_value, display_value in column_values
    }
