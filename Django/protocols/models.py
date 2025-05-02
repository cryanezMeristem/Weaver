from django.db import models
import uuid
from inventory.custom.general import COLORS
from organization.models import Project
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

REACTIVE_STATE = (
    (0, 'Solid'),
    (1, 'Liquid')
)

CONCENTRATION_UNITS = (
    ('mol', 'M'),
    ('mmol', 'mM'),
    ('grlt', 'mg / ml'),
    ('vvp', 'Volume / Volume %'),
    ('wvp', 'Weight / Volume %'),
)


class Reactive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    name = models.CharField(max_length=200)
    state = models.IntegerField(choices=REACTIVE_STATE)
    mm = models.FloatField(blank=True, null=True, help_text="g/mol")
    concentration = models.FloatField(blank=True, null=True)
    concentration_unit = models.CharField(choices=CONCENTRATION_UNITS, max_length=4, blank=True, null=True)
    is_autoclavable = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def get_state_text(self):
        reactive_state_dict = dict(REACTIVE_STATE)
        return reactive_state_dict[self.state]

    @property
    def get_concentration_text(self):
        concentration_units_dict = dict(CONCENTRATION_UNITS)
        if self.state == 0:
            # solid
            if self.mm:
                return str(self.mm) + " g/mol"
            else:
                return None
        else:
            if self.concentration:
                if self.concentration_unit:
                    return str(self.concentration) + " " + concentration_units_dict[self.concentration_unit]
                else:
                    return str(self.concentration) + " [Unkown concentration unit]"
            else:
                return 'Unknown concentration'

    @property
    def get_state_concentration_text(self):
        if self.get_concentration_text:
            return self.get_state_text + " @ " + self.get_concentration_text
        else:
            return self.get_state_text

    class Meta:
        ordering = ['name']


class Component(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    reactive = models.ForeignKey(Reactive, on_delete=models.CASCADE)
    concentration = models.FloatField()
    concentration_unit = models.CharField(choices=CONCENTRATION_UNITS, max_length=4)

    class Meta:
        ordering = ["reactive"]

    def __str__(self):
        return self.reactive.name + " - " + self.concentration.__str__() + " " + self.concentration_units

    @property
    def concentration_units(self):
        return dict(CONCENTRATION_UNITS).get(self.concentration_unit.__str__())


class TableFilter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=True)
    color = models.CharField(choices=COLORS, max_length=10, blank=True, null=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=4, validators=[MinLengthValidator(4)], unique=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    components = models.ManyToManyField(Component, blank=True)
    optional_components = models.ManyToManyField(Component, related_name='optional_components', blank=True)
    ph = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    category = models.ManyToManyField(TableFilter, blank=True, help_text="Use CTRL for multiple select")
    shared_to_project = models.ManyToManyField(Project, blank=True, help_text="Use CTRL for multiple select")

    def __str__(self):
        if self.code:
            return self.name + " | " + self.code
        else:
            return self.name

    class Meta:
        ordering = ['name']


class Variant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=4, validators=[MinLengthValidator(4)], unique=True, null=True)
    optional_components = models.ManyToManyField(Component, blank=True)
    ph = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, editable=False)

    @property
    def code_txt(self):
        final = ""
        if self.recipe.code:
            final += self.recipe.code
        final += "-"
        if self.code:
            final += self.code
        return final

    def __str__(self):
        if self.code_txt:
            return self.name + " | " + self.code_txt
        else:
            return self.name

    class Meta:
        ordering = ['name']