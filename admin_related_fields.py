# -*- coding: utf-8 -*-

__author__ = 'yablokoff'

from django.contrib import admin
from django.db import models

#
# django-admin-related-fields
# ===========================
#
# Sortable and customizable related fields in change list of Django admin.
#
# You can include fields from related models to your ModelAdmin's like this:
#
# ```python
# list_display = ('event__date', 'event__room')
# ```
#
# These fields will be sortable in admin change list.
#
# You can also specify column name for that fields and also set modifier function.
#
# Basic usage:
# ```python
# class BanquetAdmin(RelatedFieldAdmin):
#     list_display = ('event__date', 'event__room', 'start_time', 'end_time')
#
#     event__date = RelatedFieldAdminMetaclass.getter_for_related_field(
#         object_modifier=lambda obj: obj.strftime("%d.%m.%y"), name='event__date', short_description=u'Event date')
#     event__room = RelatedFieldAdminMetaclass.getter_for_related_field(
#         name='event__date', short_description=u'Event room')
# ```
#
# You can also not specify getter_for_related_field if you don't need custom short_description or object_modifier.
#


class RelatedFieldAdminMetaclass(admin.ModelAdmin.__metaclass__):
    """
    Metaclass used by RelatedFieldAdmin to handle fetching of related field values.
    We have to do this as a metaclass because Django checks that list_display fields are supported by the class.
    """
    def __getattr__(self, name):
        if '__' in name:
            getter = RelatedFieldAdminMetaclass.getter_for_related_field(name)
            setattr(self, name, getter)  # cache so we don't have to do this again
            return getter
        raise AttributeError  # let missing attribute be handled normally

    @staticmethod
    def getter_for_related_field(name, object_modifier=lambda x: x,
                                 admin_order_field=None, short_description=None):
        """
        Function that can be attached to a ModelAdmin to use as a list_display field, e.g:
        client__name = RelatedFieldAdminMetaclass.getter_for_related_field('client__name', short_description='Client').
        Object modifier can be passed - function with one parameter that can modify presentation of end object.
        I.e. one can pass function for date representation: object_modifier=lambda obj: obj.strftime("%d.%m.%y").
        """
        related_names = name.split('__')

        def getter(self, obj):
            for related_name in related_names:
                obj = getattr(obj, related_name)
            return object_modifier(obj)
        getter.admin_order_field = admin_order_field or name
        getter.short_description = short_description or related_names[-1].title().replace('_', ' ')
        return getter


class RelatedFieldAdmin(admin.ModelAdmin):
    """
    Version of ModelAdmin that can use related fields in list_display, e.g.:
    list_display = ('address__city', 'address__country__country_code')
    """
    __metaclass__ = RelatedFieldAdminMetaclass

    def queryset(self, request):
        qs = super(RelatedFieldAdmin, self).queryset(request)

        # include all related fields in queryset
        select_related = [field.rsplit('__', 1)[0] for field in self.list_display if '__' in field]

        # Include all foreign key fields in queryset.
        # This is based on ChangeList.get_query_set().
        # We have to duplicate it here because select_related() only works once.
        # Can't just use list_select_related because we might have multiple__depth__fields it won't follow.
        model = qs.model
        for field_name in self.list_display:
            try:
                field = model._meta.get_field(field_name)
            except models.FieldDoesNotExist:
                continue
            if isinstance(field.rel, models.ManyToOneRel):
                select_related.append(field_name)

        return qs.select_related(*select_related)