from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import force_text


def get_column_values(queryset, field, choices):
    if choices == 'auto':
        choices = get_field_choices(queryset, field) or _database_choices(queryset, field)
    elif choices == 'minimum':
        choices = _database_choices(queryset, field)

    return choices


def get_field_choices(queryset, field):
    field_object = _get_field(queryset.model, field)
    return getattr(field_object, 'choices', None)


def _database_choices(queryset, field):
    return [(value, force_text(value)) for value in queryset.values_list(field, flat=True).distinct().order_by(field)]


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


def default_fill(data, attribute, target_range, fill_value=None, fill_attributes=()):
    indx = 0
    new_data = list()
    fill_dict = {attribute: fill_value for attribute in fill_attributes}
    for element in target_range:

        if indx < len(data) and data[indx][attribute] == element:
            new_data.append(data[indx])
            indx += 1
        else:
            fill_record = {attribute: element}
            fill_record.update(fill_dict)
            new_data.append(fill_record)

    return new_data
