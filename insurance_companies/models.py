from django.db import models
from django.utils.translation import ugettext_lazy as _


class PriceGroup(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _('Price group')
        verbose_name_plural = _('Price groups')

    def __str__(self):
        return self.name


class Tariff(models.Model):
    district = models.ForeignKey('territories.District', on_delete=models.CASCADE, verbose_name=_("District"))
    price_group = models.ForeignKey(PriceGroup, on_delete=models.CASCADE, verbose_name=_("Price group"))

    class Meta:
        unique_together = (('district', 'price_group',),)
        verbose_name = _('Tariff')
        verbose_name_plural = _('Tariffs')
        ordering = ('price_group',)

    def __str__(self):
        return ' - '.join((str(self.district), str(self.price_group)))


class VisitTariff(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name=_("Tariff"))
    type_of_visit = models.ForeignKey('reports.TypeOfVisit', on_delete=models.CASCADE, verbose_name=_("Type of visit"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))

    class Meta:
        unique_together = (('tariff', 'type_of_visit',),)
        verbose_name = _('Visit tariff')
        verbose_name_plural = _('Visit tariffs')

    def __str__(self):
        return ' - '.join((str(self.tariff), str(self.type_of_visit)))


class Company(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name=_("Name"))
    price_group = models.ForeignKey(PriceGroup, on_delete=models.PROTECT, verbose_name=_("Price group"))
    initials = models.CharField(max_length=3, verbose_name=_("Initials"), blank=True)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return self.name
