django-admin-related-fields
===========================

Sortable and customizable related fields in change list of Django admin.

You can include fields from related models to your ModelAdmin's like this:

```python
list_display = ('event__date', 'event__room')
```

These fields will be sortable in admin change list.

You can also specify column name for that fields and also set modifier function.

Basic usage:
```python
class BanquetAdmin(RelatedFieldAdmin):
    list_display = ('event__date', 'event__room', 'start_time', 'end_time')

    event__date = RelatedFieldAdminMetaclass.getter_for_related_field(
        object_modifier=lambda obj: obj.strftime("%d.%m.%y"), name='event__date', short_description=u'Event date')
    event__room = RelatedFieldAdminMetaclass.getter_for_related_field(
        name='event__date', short_description=u'Event room')
```

You can also not specify getter_for_related_field if you don't need custom short_description or object_modifier.