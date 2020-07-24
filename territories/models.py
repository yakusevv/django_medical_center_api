from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name=_("Country"))
    is_city_state = models.BooleanField(default=False, verbose_name=_("City-state"))

    class Meta:
        unique_together = (('name', 'country',),)
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    region = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name=_("Region"))

    class Meta:
        unique_together = (('name', 'region',),)
        verbose_name = _('District')
        verbose_name_plural = _('Districts')

    def __str__(self):
        return ' - '.join((str(self.region), self.name))


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    district = models.ForeignKey(District, on_delete=models.PROTECT, verbose_name=_("District"))

    class Meta:
        unique_together = (('name', 'district',),)
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return ' - '.join((str(self.name), str(self.district.region.country)))

    def validate_unique(self, exclude=None):
        qs = City.objects.filter(district__region__country=self.district.region.country)
        if self.pk is None:
            if qs.filter(name=self.name).exists():
                raise ValidationError(_("City with this name in the current country is already exists"))

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(City, self).save(*args, **kwargs)

