from django.db.models import Case, When, Q, F, Sum, CharField
from django.db.models import Value
from django.shortcuts import _get_queryset

from django_pivot.utils import get_column_values, get_field_choices


def pivot(queryset, row, column, data, aggregation=Sum, choices='auto'):
    """
    Takes a queryset and pivots it. The result is a table with one record
    per unique value in the `row` column, a column for each unique value in the `column` column
    and values in the table aggregated by the data column.

    :param queryset: a QuerySet, Model, or Manager
    :param row: string, name of column that will key the rows
    :param column: string, name of column that will define columns
    :param data: column name or Combinable
    :param aggregation: aggregation function to apply to data column
    :return: ValuesQueryset
    """
    queryset = _get_queryset(queryset)

    column_values = get_column_values(queryset, column, choices)

    annotations = _get_annotations(column, column_values, data, aggregation)

    values = [row]

    row_choices = get_field_choices(queryset, row)
    if row_choices:
        whens = (When(Q(**{row: value}), then=Value(display_value, output_field=CharField())) for value, display_value in row_choices)
        row_display = Case(*whens)
        queryset = queryset.annotate(**{'get_' + row + '_display': row_display})
        values.append('get_' + row + '_display')

    return queryset.values(*values).annotate(**annotations)


def _get_annotations(column, column_values, data, aggregation):
    value = data if hasattr(data, 'resolve_expression') else F(data)
    return {
        display_value: aggregation(Case(When(Q(**{column: column_value}), then=value)))
        for column_value, display_value in column_values
    }
