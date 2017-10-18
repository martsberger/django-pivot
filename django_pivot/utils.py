from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import force_text


def get_column_values(queryset, field, choices):
    field_object = _get_field(queryset.model, field)
    if choices == 'auto' and getattr(field_object, 'choices', None):
        field_values = field_object.choices
    elif choices == 'auto' or choices == 'minimum':
        database_values = queryset.values_list(field, flat=True).distinct().order_by(field)
        field_values = [(field_value, force_text(field_value)) for field_value in database_values]
    else:
        field_values = choices

    return field_values


def _get_field(model, field_names):
    field_list = field_names.split('__')
    for field_name in field_list:
        try:
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist:
            # This can happen when we slice_on an annotated field
            return None
        if field.is_relation:
            model = field.related_model
        else:
            return field
