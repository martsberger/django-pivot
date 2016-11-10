from django.db.models import Case, When, Q, Count
from django.shortcuts import _get_queryset
from django.utils.encoding import force_text


def histogram(queryset, column, bins):
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
        force_text(bins[k]): between_include_start(column, bins[k], bins[k + 1])
        for k in range(len(bins) - 1)
    }
    aggregations[force_text(bins[-1])] = Count(Case(When(Q(**{column + '__gte': bins[-1]}), then=1)))

    return queryset.aggregate(**aggregations)


def between_include_start(column, start, end):
    return Count(Case(When(Q(**{column + '__gte': start,
                                column + '__lt': end}), then=1)))
