from django import forms
from .models import Recipe
from .models import Variant
from .models import Component
from .models import Reactive
from organization.views import get_projects_where_member_can_write_or_admin
from django.shortcuts import get_object_or_404

RECIPE_UNITS = (
    ('ml', 'ml'),
    ('lt', 'lt'),
)


class ComponentCreateForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = '__all__'
        exclude = ['owner']


def get_member_components(member):
    return Component.objects.filter(owner=member)


def get_member_reactives(member):
    return Reactive.objects.filter(owner=member)


class VariantCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        recipe_id = kwargs.pop('recipe_id')
        super(VariantCreateForm, self).__init__(*args, **kwargs)
        recipe = Recipe.objects.get(id=recipe_id)
        self.fields['optional_components'].queryset = recipe.optional_components

    class Meta:
        model = Variant
        fields = '__all__'


class VariantEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VariantEditForm, self).__init__(*args, **kwargs)
        self.fields['optional_components'].queryset = self.instance.recipe.optional_components

    class Meta:
        model = Variant
        fields = '__all__'
        exclude = ['recipe']


class RecipeCreateEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        member = kwargs.pop('user')
        super(RecipeCreateEditForm, self).__init__(*args, **kwargs)
        self.fields['components'].queryset = get_member_components(member)
        self.fields['shared_to_project'].queryset = get_projects_where_member_can_write_or_admin(member)

    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = ['owner']


class ComponentCreateEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        member = kwargs.pop('user')
        super(ComponentCreateEditForm, self).__init__(*args, **kwargs)
        self.fields['reactive'].queryset = get_member_reactives(member)

    class Meta:
        model = Component
        fields = '__all__'
        exclude = ['owner']


class RecipeVariantForm(forms.Form):
    quantity = forms.FloatField(label='Quantity')
    unit = forms.ChoiceField(label='Unit', choices=RECIPE_UNITS)
    concentration = forms.FloatField(label='Concentration', required=False, initial=1)
