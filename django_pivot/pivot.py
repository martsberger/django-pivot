from django.db.models import Case, When, Q, F, Sum, CharField, Value
from django.db.models.functions import Coalesce
from django.shortcuts import _get_queryset

from django_pivot.utils import get_column_values, get_field_choices, default_fill


def pivot(queryset, rows, column, data, aggregation=Sum, choices='auto', display_transform=lambda s: s,
          default=None, row_range=(), ordering=(), include_total=False):
    """
    Takes a queryset and pivots it. The result is a table with one record
    per unique value in the `row` column, a column for each unique value in the `column` column
    and values in the table aggregated by the data column.

    :param queryset: a QuerySet, Model, or Manager
    :param rows: list of strings, name of columns that will key the rows
    :param column: string, name of column that will define columns
    :param data: column name or Combinable
    :param aggregation: aggregation function to apply to data column
    :param choices: specify 'minimum' if you want to do an extra database query to get only choices present in the data
    :param display_transform: function that takes an object and returns a string
    :param default: default value to pass to the aggregate function when no record is found
    :param row_range: iterable with the expected range of rows in the result
    :param ordering: option to specify how the resulting pivot should be ordered
    :param include_total: Boolean, default False, add an additional column containing the Total of the aggregation
    :return: ValuesQueryset
    """
    values = [rows] if isinstance(rows, str) else list(rows)

    queryset = _get_queryset(queryset).order_by(*ordering)

    column_values = get_column_values(queryset, column, choices)

    annotations = _get_annotations(column, column_values, data, aggregation, display_transform,
                                   default=default, include_total=include_total)
    for row in values:
        row_choices = get_field_choices(queryset, row)
        if row_choices:
            whens = (When(Q(**{row: value}), then=Value(display_value, output_field=CharField()))
                     for value, display_value in row_choices)
            row_display = Case(*whens)
            queryset = queryset.annotate(**{'get_' + row + '_display': row_display})
            values.append('get_' + row + '_display')

    column_alias_map = {
        f'CA{n}': annotation_alias for n, annotation_alias in enumerate(annotations.keys())
    }

    annotations = _swap_dictionary_keys(annotations, column_alias_map, reverse=True)

    values_list = [_swap_dictionary_keys(result, column_alias_map)
                   for result in queryset.values(*values).annotate(**annotations)]

    if row_range:
        attributes = [value[0] for value in column_values]
        values_list = default_fill(values_list, values[0], row_range, fill_value=default, fill_attributes=attributes)

    return values_list


def _get_annotations(column, column_values, data, aggregation, display_transform=lambda s: s,
                     default=None, include_total=False):
    value = data if hasattr(data, 'resolve_expression') else F(data)
    kwargs = dict()
    if hasattr(data, 'output_field'):
        kwargs['output_field'] = data.output_field
    annotations = {
        display_transform(display_value): Coalesce(aggregation(Case(When(Q(**{column: column_value}), then=value))), default, **kwargs)
        for column_value, display_value in column_values
    }
    if include_total:
        annotations['Total'] = Coalesce(aggregation(value), default, **kwargs)

    return annotations


def _swap_dictionary_keys(dictionary, key_map, reverse=False):
    """
    Change the keys of a dictionary to different keys based on a key map.
    Preserves key, value pairs for keys not found in key_map.
    If `reverse` is True, the key_map is used in the opposite direction, keys
    and values are switched.

    :param dictionary: the input dictionary
    :param key_map: a mapping from the keys in the input dictionary to a new set of keys
    :param reverse: Boolean indicating whether the key_map should be reversed
    :return: A new dictionary with the old keys replaced by the keys in key_map
    """
    if reverse:
        key_map = {v: k for k, v in key_map.items()}

    return {
        key_map.get(key, key): dictionary[key]
        for key in dictionary.keys()
    }
