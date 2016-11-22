from django.db.models import Case, When, Q, F, Sum
from django.shortcuts import _get_queryset
from django.utils.encoding import force_text


def pivot(queryset, row, column, data, aggregation=Sum):
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

    column_values = _get_column_values(queryset, column).order_by(column)

    annotations = _get_annotations(column, column_values, data, aggregation)

    return queryset.values(row).annotate(**annotations)


def _get_column_values(queryset, column):
    return queryset.values_list(column, flat=True).distinct()


def _get_annotations(column, column_values, data, aggregation):
    value = data if hasattr(data, 'resolve_expression') else F(data)
    return {
        force_text(c): aggregation(Case(When(Q(**{column: c}), then=value)))
        for c in column_values
    }
