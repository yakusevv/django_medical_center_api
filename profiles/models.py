from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    city = models.ForeignKey('territories.City', on_delete=models.SET_NULL, null=True, verbose_name=_("City"))
    num_col = models.CharField(max_length=9, verbose_name=_("Num. col"))
    is_foreign_doctor = models.BooleanField(default=False, verbose_name=_("Is foreign doctor"))
    initials = models.CharField(max_length=5, verbose_name=_("Initials"), blank=True)
    viber_id = models.CharField(max_length=100, verbose_name=_("Viber id"), blank=True,)
    is_owner = models.BooleanField(default=False, verbose_name=_("Owner"))

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def validate_unique(self, *args, **kwargs):
        super(Profile, self).validate_unique(*args, **kwargs)

        if self.__class__.objects.filter(
                    initials=self.initials,
                    city__district__region__country=self.city.district.region.country
                    ).exclude(pk=self.pk).exists():
            raise ValidationError(
                message=_('Profile with this initials in current country is already exists.'),
                code='unique_together',
            )

        if self.__class__.objects.filter(
                    num_col=self.num_col,
                    city__district__region__country=self.city.district.region.country
                    ).exclude(pk=self.pk).exists():
            raise ValidationError(
                message=_('Profile with this Num. col. in current country is already exists.'),
                code='unique_together',
            )

    def __str__(self):
        return ' '.join((self.user.last_name, self.user.first_name, self.num_col))

    def get_absolute_url(self):
        return reverse('profile_detail_url', kwargs={'pk': self.pk})


class ReportAutofillTemplate(models.Model):
    profile = models.ForeignKey(
                            Profile,
                            related_name='report_templates',
                            on_delete=models.CASCADE,
                            verbose_name=_("Doctor")
                            )
    country = models.ForeignKey(
                            'territories.Country',
                            related_name='report_templates',
                            on_delete=models.CASCADE,
                            verbose_name=_("Country")
                            )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    cause_of_visit_template = models.TextField(max_length=700, blank=True, verbose_name=_("Cause of visit"))
    checkup_template = models.TextField(max_length=1200, blank=True, verbose_name=_("Checkup"))
    additional_checkup_template = models.TextField(max_length=700, blank=True, verbose_name=_("Additional checkup"))
    prescription_template = models.TextField(max_length=700, blank=True, verbose_name=_("Prescription"))
    diagnosis_template = models.ManyToManyField(
                                            'reports.Disease',
                                            related_name='autofill_template',
                                            verbose_name=_("Diagnosis"),
                                            blank=True
                                            )

    class Meta:
        unique_together = (('profile', 'name',),)
        verbose_name = _('Report autofill template')
        verbose_name_plural = _('Report autofill templates')

    def get_update_url(self):
        return reverse('profile_template_update_url', kwargs={'pk': self.pk})


class DoctorDistrict(models.Model):
    doctor = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name=_("Doctor"))
    cities = models.ManyToManyField('territories.City', related_name='cities', verbose_name=_("Cities"))
    country = models.ForeignKey(
                            'territories.Country',
                            related_name='doctor_district',
                            verbose_name=_("Country"),
                            on_delete=models.CASCADE
                            )

    class Meta:
        verbose_name = _('District coverage')
        verbose_name_plural = _('Districts coverage')

    def __str__(self):
        return ' - '.join((str(self.doctor), 'district', str(str(self.cities.all()[0].name) + '...')))


class DoctorDistrictVisitPrice(models.Model):
    doctor_district = models.ForeignKey(DoctorDistrict, on_delete=models.CASCADE, verbose_name=_("District"))
    type_of_visit = models.ForeignKey('reports.TypeOfVisit', on_delete=models.CASCADE, verbose_name=_("Type of visit"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))

    class Meta:
        unique_together = (('doctor_district', 'type_of_visit'),)
        verbose_name = _('Visit price for the doctor')
        verbose_name_plural = _('Visit prices for the doctors')

    def __str__(self):
        return ' - '.join((str(self.doctor_district), str(self.type_of_visit)))

