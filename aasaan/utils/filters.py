from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter, RelatedOnlyFieldListFilter
)


class DropdownFilter(AllValuesFieldListFilter):
    template = 'common/dropdown_filter.html'


class ChoiceDropdownFilter(ChoicesFieldListFilter):
    template = 'common/dropdown_filter.html'


class RelatedDropdownFilter(RelatedFieldListFilter):
    template = 'common/dropdown_filter.html'


class RelatedOnlyDropdownFilter(RelatedOnlyFieldListFilter):
    template = 'common/dropdown_filter.html'
