from django.db import models
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class InsuranceCase(models.Model):
    STATUS = (
        ('accepted', _('Is accepted')),
        ('cancelled_by_company', _('Cancelled by company')),
        ('wrong_data', _('Wrong request data')),
        ('failed', _('The visit did not take place')),
    )

    doctor = models.ForeignKey(
                                'profiles.Profile',
                                on_delete=models.PROTECT,
                                verbose_name=_("Doctor"),
                                related_name="Cases",
                                blank=True
                                )
    date_time = models.DateTimeField(verbose_name=_("Date and time"))
    message = models.TextField(max_length=500, verbose_name=_("Message"))
    seen = models.BooleanField(default=False)
    ref_number = models.PositiveIntegerField(verbose_name=_("Ref. number"))
    company = models.ForeignKey('insurance_companies.Company', on_delete=models.PROTECT, verbose_name=_("Company"))
    sender = models.ForeignKey('profiles.Profile', on_delete=models.PROTECT, verbose_name=_('Sender'))
    status = models.CharField(max_length=20, choices=STATUS, default='accepted', verbose_name=_('Status'))

    class Meta:
        verbose_name = _('Insurance Case')
        verbose_name_plural = _('Insurance Cases')

    def validate_unique(self, exclude=None):
        country = self.doctor.city.district.region.country
        qs = InsuranceCase.objects.filter(
                                            doctor__city__district__region__country=country,
                                            company=self.company,
                                            ref_number=self.ref_number,
                                            date_time__year=self.date_time.year
                                         )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                                _("Case {}{} is already exists".format(
                                                                    self.company.initials,
                                                                    str(self.ref_number).zfill(3))
                                  )
                                 )

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(InsuranceCase, self).save(*args, **kwargs)

    def __str__(self):
        return ' '.join((
                        str(self.company.initials),
                        str(self.ref_number).zfill(3),
                        str(' '.join(self.message.split()[:2])),
                        str(self.date_time.strftime('%d.%m.%Y %H:%M')),
                        str(self.doctor.initials)
                        ))

    def has_report(self):
        return hasattr(self, 'report') and self.report is not None

    def get_update_url(self):
        return reverse('report_request_update_url', kwargs={'pk': self.pk})

