from django.db.models import Case, When, Q, Count, IntegerField, CharField
from django.db.models import Value
from django.shortcuts import _get_queryset
from django.utils.encoding import force_text

from django_pivot.utils import get_column_values


def histogram(queryset, column, bins, slice_on=None, choices='auto'):
    if slice_on is None:
        return simple_histogram(queryset, column, bins)
    else:
        return multi_histogram(queryset, column, bins, slice_on, choices)


def simple_histogram(queryset, column, bins):
    """
    Return a histogram from data in queryset.

    :param queryset: A Queryet, Model, or Manager
    :param column: The column we are aggregating into a histogram
    :param bins: An ordered iterable of left endpoints of the bins. Must have at least two elements.
    The endpoints must be a convertible to strings by force_text
    :return: A dictionary with bin endpoints converted to strings as keys and
    """
    queryset = _get_queryset(queryset)

    queryset = queryset.annotate(column_name=Value(column, output_field=CharField()))

    return multi_histogram(queryset, column, bins, slice_on='column_name', choices=((column, column),))


def between_include_start(column, start, end, value=1):
    return When(Q(**{column + '__gte': start, column + '__lt': end}), then=value)


def multi_histogram(queryset, column, bins, slice_on, choices):
    """
    Returns a table of histograms, one for each unique value of field in queryset.

    :param queryset:  A Queryet, Model, or Manager
    :param column: The column we are aggregating into a histogram
    :param bins: An ordered iterable of left endpoints of the bins. Must have at least two elements.
    The endpoints must be a convertible to strings by force_text
    :param slice_on: A field of the queryset that we are slicing the histograms on
    :return: A ValuesQuerySet
    """
    queryset = _get_queryset(queryset)

    field_values = get_column_values(queryset, slice_on, choices)

    bins = [force_text(bin) for bin in bins]

    whens = tuple(
        between_include_start(column, bins[k], bins[k+1], Value(force_text(bins[k])))
        for k in range(len(bins) - 1)
    ) + (
        When(Q(**{column + '__gte': bins[-1]}), Value(force_text(bins[-1]))),
    )

    ordering_whens = tuple(
        between_include_start(column, bins[k], bins[k + 1], Value(k))
        for k in range(len(bins) - 1)
    ) + (
        When(Q(**{column + '__gte': bins[-1]}), Value(len(bins) - 1)),
    )

    bin_annotation = {
        'bin': Case(*whens, output_field=CharField()),
        'order': Case(*ordering_whens, output_field=IntegerField())
    }

    histogram_annotation = {
        display_value: Count(Case(When(Q(**{slice_on: field_value}), then=1), output_field=IntegerField()))
        for field_value, display_value in field_values
    }

    qs = queryset.annotate(**bin_annotation).order_by('order').values('bin').filter(bin__isnull=False).annotate(**histogram_annotation)

    return _zero_fill(qs, bins, field_values)


def _zero_fill(qs, bins, field_values):
    """
    If a bin has zero counts for every histogram, there is no mechanism in SQL
    to get a record for this bin from just the table being queried. (The SQL
    workaround is to create a temp table of bins and join to it -- gross.)

    :param qs: This histogram queryset with zeros missing
    :param bins: The left edges of the bins as passed to histogram
    :param field_values: A list of tuples for the choices of the slice_on field
    :return: A list of dictionaries with the zero values filled in
    """
    zeros = {display_value: 0 for field_value, display_value in field_values}

    iter_qs = iter(qs)

    result = []
    next_bin = next(iter_qs)

    for binn in bins:
        if next_bin['bin'] == binn:
            result.append(next_bin)
            try:
                next_bin = next(iter_qs)
            except StopIteration:
                pass
        else:
            this_bin = {'bin': binn}
            this_bin.update(zeros)
            result.append(this_bin)

    return result
