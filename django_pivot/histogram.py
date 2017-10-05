from django.db.models import Case, When, Q, Count, IntegerField, CharField
from django.db.models import Value
from django.shortcuts import _get_queryset
from django.utils.encoding import force_text


def histogram(queryset, column, bins, field=None):
    if field is None:
        return simple_histogram(queryset, column, bins)
    else:
        return multi_histogram(queryset, column, bins, field)


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

    aggregations = {
        force_text(bins[k]): Count(Case(between_include_start(column, bins[k], bins[k + 1])))
        for k in range(len(bins) - 1)
    }
    aggregations[force_text(bins[-1])] = Count(Case(When(Q(**{column + '__gte': bins[-1]}), then=1)))

    return queryset.aggregate(**aggregations)


def between_include_start(column, start, end, value=1):
    return When(Q(**{column + '__gte': start, column + '__lt': end}), then=value)


def multi_histogram(queryset, column, bins, field):
    """
    Returns a table of histograms, one for each unique value of field in queryset.

    :param queryset:  A Queryet, Model, or Manager
    :param column: The column we are aggregating into a histogram
    :param bins: An ordered iterable of left endpoints of the bins. Must have at least two elements.
    The endpoints must be a convertible to strings by force_text
    :param field: A field of the queryset that we are slicing the histograms on
    :return: A ValuesQuerySet
    """
    queryset = _get_queryset(queryset)

    field_values = queryset.values_list(field, flat=True)

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
        field_value: Count(Case(When(Q(**{field: field_value}), then=1), output_field=IntegerField()))
        for field_value in field_values
    }

    return queryset.annotate(**bin_annotation).order_by('order').values('bin').filter(bin__isnull=False).annotate(**histogram_annotation)
