from django.shortcuts import render
from django.utils.decorators import method_decorator
from .models import Recipe
from .models import Variant
from .models import Component
from .models import Reactive
from .models import TableFilter
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .models import CONCENTRATION_UNITS
from .forms import RecipeVariantForm
from .forms import RecipeCreateEditForm
from .forms import VariantCreateForm
from .forms import VariantEditForm
from .forms import ComponentCreateForm
from .forms import ComponentCreateEditForm
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.urls import reverse
import datetime
from .decorators import require_member_own_recipe
from .decorators import require_member_own_variant
from .decorators import require_member_own_reactive
from .decorators import require_member_own_component
from .decorators import require_member_can_view_recipe
from .decorators import require_member_can_view_variant
from organization.views import get_show_from_all_projects
from organization.views import get_projects_where_member_can_any
from organization.decorators import require_current_project_set
from django.db.models import Q
from django.shortcuts import get_object_or_404


def can_member_edit_recipe(recipe, member):
    return True if recipe.owner == member else False


def process_recipe_variant_post(recipe_variant_form, recipe_variant_to_detail):
    context = {
        'result': [],
        'warnings': [],
        'quantity': recipe_variant_form.cleaned_data['quantity'],
        'quantity_unit': recipe_variant_form.cleaned_data['unit'],
        'concentration': recipe_variant_form.cleaned_data['concentration'],
    }

    any_not_autoclavable = False

    # lt to prepare
    quantity = int(recipe_variant_form.cleaned_data['quantity']) * int(context['concentration'])

    if context['quantity_unit'] == 'ml':
        quantity /= 1000

    if recipe_variant_to_detail.__class__.__name__ == "Recipe":
        all_components = list(recipe_variant_to_detail.components.all())
    else:
        # Variant
        all_components = list(recipe_variant_to_detail.recipe.components.all()) + list(recipe_variant_to_detail.optional_components.all())

    for component in all_components:
        # default
        component_unit = "-"
        component_mass_or_volume = "Unable to calculate."

        component_error = None

        # state based
        if component.reactive.state == 0:
            # solid
            if component.concentration_unit == 'vvp':
                component_error = "Can not convert solid reactive to volume / volume units"
            elif component.concentration_unit in ['mol', 'mmol']:
                if component.reactive.mm:
                    component_unit = 'gr'
                    component_mass_or_volume = component.reactive.mm * component.concentration * quantity
                    if component.concentration_unit == 'mmol':
                        component_mass_or_volume /= 1000
                else:
                    component_error = "No molar mass set. It's required to calculate."
            else:
                # grlt or wvp
                component_unit = 'gr'
                component_mass_or_volume = component.concentration * quantity
                if component.concentration_unit == 'wvp':
                    component_mass_or_volume *= 10
        else:
            # liquid

            # tramsform units
            if component.concentration_unit == 'mmol':
                component.concentration_unit = 'mol'
                component.concentration /= 1000
            if component.reactive.concentration_unit == 'mmol':
                component.reactive.concentration_unit = 'mol'
                component.reactive.concentration /= 1000
            if component.concentration_unit == 'wpv':
                component.concentration_unit = 'grlt'
                component.concentration *= 10
            if component.reactive.concentration_unit == 'wpv':
                component.reactive.concentration_unit = 'grlt'
                component.reactive.concentration *= 10

            if component.concentration_unit == 'vvp':
                # quantity in liters, multiply by 10. Divide by 1000 to get the liters
                component_mass_or_volume = quantity * component.concentration / 100
                component_unit = 'lt'
            else:
                if component.concentration_unit != component.reactive.concentration_unit:
                    if component.reactive.concentration_unit == 'vvp':
                        component_error = 'Unable con convert volume / volume to mass / volume units'
                    else:
                        if component.reactive.mm:
                            # diferent units, convert
                            if component.concentration_unit == 'mol':
                                component.concentration_unit = 'grlt'
                                component.concentration *= component.reactive.mm
                            if component.reactive.concentration_unit == 'mol':
                                component.reactive.concentration_unit = 'grlt'
                                component.reactive.concentration *= component.reactive.mm
                        else:
                            component_error = 'Reactive molar mass is required'

            if component.concentration_unit == component.reactive.concentration_unit:
                # check again in case no mm is set above
                if component.reactive.concentration > component.concentration:
                    component_unit = 'lt'
                    component_mass_or_volume = component.concentration * quantity / component.reactive.concentration
                else:
                    component_error = 'Stock concentration is equal or lower than component concentration'

        # adjust units
        if (type(component_mass_or_volume) == int or type(
                component_mass_or_volume) == float) and component_mass_or_volume < 1:
            component_mass_or_volume *= 1000
            if component_unit == 'gr':
                component_unit = 'mg'
            if component_unit == 'lt':
                component_unit = 'ml'
                if component_mass_or_volume < 1:
                    component_mass_or_volume *= 1000
                    component_unit = 'ul'

        # autoclavable reactives
        if not component.reactive.is_autoclavable:
            any_not_autoclavable = True

        if component_error:
            context['result'].append((component.reactive, component_error, component_unit, True))
        else:
            context['result'].append((component.reactive, component_mass_or_volume, component_unit, False))

    context['any_not_autoclavable'] = any_not_autoclavable
    return context


@require_current_project_set
@require_member_can_view_variant
def variant(request, variant_id):
    try:
        variant_to_detail = Variant.objects.get(id=variant_id)
    except ObjectDoesNotExist:
        raise Http404

    context = {}
    if request.method == 'POST':
        recipe_form = RecipeVariantForm(request.POST)
        if recipe_form.is_valid():
            context = process_recipe_variant_post(recipe_form, variant_to_detail)

    context['variant'] = variant_to_detail
    context['user_can_edit_variant'] = can_member_edit_recipe(variant_to_detail.recipe, request.user)
    context['recipe_form'] = RecipeVariantForm()

    return render(request, 'protocols/variant.html', context)


@require_member_can_view_variant
def variant_label(request, variant_id):
    try:
        variant_to_label = Variant.objects.get(id=variant_id)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'variant': variant_to_label,
        'recipe': variant_to_label.recipe,
        'date': datetime.datetime.now().date(),
        'CONCENTRATION_UNITS_dict': dict(CONCENTRATION_UNITS),
        'user_can_edit_variant': can_member_edit_recipe(variant_to_label.recipe, request.user)
    }
    return render(request, 'protocols/variant_label.html', context)


class VariantCreate(CreateView):
    model = Variant
    form_class = VariantCreateForm
    template_name_suffix = '_create_form'

    @method_decorator(require_member_own_recipe)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.recipe = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(VariantCreate, self).get_form_kwargs()
        kwargs.update({'recipe_id': self.kwargs['recipe_id']})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipe"] = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        return context

    def get_success_url(self, **kwargs):
        return reverse('recipe', args=(self.object.recipe.id,)) + '?form_result_recipe_edit_success=true'


class VariantEdit(UpdateView):
    model = Variant
    form_class = VariantEditForm
    template_name_suffix = '_update_form'

    @method_decorator(require_member_own_variant)
    def dispatch(self, *args, **kwargs):
        self.extra_context = {
            'show_create_component_button': True
        }
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_can_edit_variant'] = can_member_edit_recipe(self.object.recipe, self.request.user)
        context['component_form'] = ComponentCreateForm()
        return context

    def get_form_kwargs(self):
        kwargs = super(VariantEdit, self).get_form_kwargs()
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse('variant', args=(self.object.id,)) + '?form_result_recipe_edit_success=true'


class VariantDelete(DeleteView):
    model = Variant

    @method_decorator(require_member_own_variant)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_can_edit_variant'] = can_member_edit_recipe(self.object.recipe, self.request.user)
        return context

    def get_success_url(self, **kwargs):
        return reverse('recipes') + '?form_result_object_deleted=true'


@require_current_project_set
@require_member_can_view_recipe
def recipe(request, recipe_id):
    try:
        recipe_to_detail = Recipe.objects.get(id=recipe_id)
    except ObjectDoesNotExist:
        raise Http404

    context = {}
    if request.method == 'POST':
        recipe_form = RecipeVariantForm(request.POST)
        if recipe_form.is_valid():
            context = process_recipe_variant_post(recipe_form, recipe_to_detail)

    context['recipe'] = recipe_to_detail
    context['user_can_edit_recipe'] = can_member_edit_recipe(recipe_to_detail, request.user)
    context['recipe_form'] = RecipeVariantForm()

    return render(request, 'protocols/recipe.html', context)


def recipes(request):
    options = []
    for recipe_cat in TableFilter.objects.all():
        options.append((recipe_cat.name, recipe_cat.name, recipe_cat.color))
    table_filters = [
        ['all', 'All', [
            ('All', 'all', 'primary'),
        ]],
        ['category', 'Category', options],
    ]
    if get_show_from_all_projects(request):
        recipes = Recipe.objects.filter(Q(owner=request.user) | Q(shared_to_project__in=get_projects_where_member_can_any(request.user))).distinct()
    else:
        recipes = Recipe.objects.filter(owner=request.user)

    for recipe in recipes:
        recipe.user_can_edit_recipe = can_member_edit_recipe(recipe, request.user)
    
    context = {
        'recipes': recipes,
        'table_filters': table_filters,
        'show_from_all_projects': get_show_from_all_projects(request)
    }
    return render(request, 'protocols/recipes.html', context)


class RecipeEdit(UpdateView):
    model = Recipe
    form_class = RecipeCreateEditForm
    template_name_suffix = '_update_form'

    @method_decorator(require_member_own_recipe)
    def dispatch(self, *args, **kwargs):
        self.extra_context = {
            'show_create_component_button': True
        }
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_can_edit_recipe'] = can_member_edit_recipe(self.object, self.request.user)
        context['component_form'] = ComponentCreateForm()
        return context

    def get_form_kwargs(self):
        kwargs = super(RecipeEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse('recipe', args=(self.object.id,)) + '?form_result_recipe_edit_success=true'


class RecipeDelete(DeleteView):
    model = Recipe

    @method_decorator(require_member_own_recipe)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_can_edit_recipe'] = can_member_edit_recipe(self.object, self.request.user)
        return context

    def get_success_url(self, **kwargs):
        return reverse('recipes') + '?form_result_object_deleted=true'


class RecipeCreate(CreateView):
    model = Recipe
    form_class = RecipeCreateEditForm
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(RecipeCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse('recipes') + '?form_result_recipe_create_success=true'


@require_member_can_view_recipe
def recipe_label(request, recipe_id):
    try:
        recipe_to_label = Recipe.objects.get(id=recipe_id)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'recipe': recipe_to_label,
        'date': datetime.datetime.now().date(),
        'CONCENTRATION_UNITS_dict': dict(CONCENTRATION_UNITS),
        'user_can_edit_recipe': can_member_edit_recipe(recipe_to_label, request.user)
    }
    return render(request, 'protocols/recipe_label.html', context)


class ComponentEdit(UpdateView):
    model = Component
    fields = '__all__'
    template_name_suffix = '_update_form'

    @method_decorator(require_member_own_component)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('recipe', args=(self.kwargs['recipe_id'],)) + '?form_result_component_edit_success=true'


class ComponentCreate(CreateView):
    model = Component
    form_class = ComponentCreateEditForm
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ComponentCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse('recipe_create') + '?form_result_component_create_success=true'


class ComponentCreateReturnToRecipe(CreateView):
    model = Component
    form_class = ComponentCreateEditForm
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ComponentCreateReturnToRecipe, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self, **kwargs):
        return reverse('recipe_edit', args=(self.kwargs['recipe_id'],)) + '?form_result_component_create_success=true'


class ComponentDelete(DeleteView):
    model = Component

    @method_decorator(require_member_own_component)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('recipe', args=(self.kwargs['recipe_id'],)) + '?form_result_component_edit_success=true'


class ReactiveCreate(CreateView):
    model = Reactive
    fields = '__all__'
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('component_create') + '?form_result_reactive_create_success=true'


class ReactiveCreateReturnToRecipe(CreateView):
    model = Reactive
    fields = '__all__'
    template_name_suffix = '_create_form'

    def form_valid(self, form):
        print(self.request.user)
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('recipe_edit', args=(self.kwargs['recipe_id'],)) + '?form_result_reactive_create_success=true'


class ReactiveEdit(UpdateView):
    model = Reactive
    fields = '__all__'
    template_name_suffix = '_update_form'

    @method_decorator(require_member_own_reactive)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('recipe',
                       args=(self.kwargs['recipe_id'],)) + '?form_result_reactive_edit_success=true'


class ReactiveDelete(DeleteView):
    model = Reactive

    @method_decorator(require_member_own_reactive)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse('recipe',
                       args=(self.kwargs['recipe_id'],)) + '?form_result_reactive_edit_success=true'



def index(request):
    context = {
    }
    return render(request, 'protocols/index.html', context)
