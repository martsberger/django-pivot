from django.db.models import Case, When, Q, F, Sum


def pivot(queryset, row, column, data):
    """
    Takes a queryset and pivots it. The result is a table with one record
    per unique value in the row column, a column for each unique value in the column column
    and values in the table aggregated by data.

    :param queryset:
    :param row:
    :param column:
    :param data:
    :return: ValuesQueryset
    """

    columns = queryset.values_list(column, flat=True).distinct()

    annotations = {
        c: Sum(Case(When(Q(**{column: c}), then=F(data))))
        for c in columns
    }

    return queryset.values(row).annotate(**annotations)
