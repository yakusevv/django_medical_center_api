import os
import shutil

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


def get_image_path(instance, filename):
    return os.path.join(
                    'FILES',
                    str(instance.report.pk),
                    filename
                    )


def get_docxtemplate_path(instance, filename):
    filename = str(instance.country.name) + '_template.docx'
    return os.path.join('DOC_TEMPLATES', filename)


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name

    def __str__(self):
        return self.name


class Disease(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=_("Name"))
    country = models.ForeignKey('territories.Country', on_delete=models.PROTECT, verbose_name=_("Country"))

    class Meta:
        verbose_name = _('Disease')
        verbose_name_plural = _('Diseases')

    def __str__(self):
        return self.name


class TypeOfVisit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    short_name = models.CharField(max_length=50, verbose_name=_("Short name"), blank=True)
    is_second_visit = models.BooleanField(default=False, verbose_name=_("Is second visit"))
    country = models.ForeignKey('territories.Country', on_delete=models.PROTECT, verbose_name=_("Country"))
    initial = models.CharField(max_length=2, verbose_name=_("Initial"), blank=True)

    class Meta:
        unique_together = (('name', 'country',),)
        verbose_name = _('Type of visit')
        verbose_name_plural = _('Types of visits')

    def __str__(self):
        if self.short_name:
            return self.short_name
        else:
            return self.name


class ReportTemplate(models.Model):
    template = models.FileField(upload_to=get_docxtemplate_path, storage=OverwriteStorage(), verbose_name=_("Template"))
    country = models.OneToOneField('territories.Country', on_delete=models.CASCADE, verbose_name=_("Country"))

    class Meta:
        verbose_name = _('Report template')
        verbose_name_plural = _('Report templates')


class Report(models.Model):
    company_ref_number = models.CharField(max_length=50, verbose_name=_("Company ref. number"))
    patients_first_name = models.CharField(max_length=50, verbose_name=_("First name"))
    patients_last_name = models.CharField(max_length=50, verbose_name=_("Last name"))
    patients_date_of_birth = models.DateField(verbose_name=_("Date of birth"))
    patients_policy_number = models.CharField(max_length=100, blank=True, verbose_name=_("Policy number"))
    type_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.PROTECT, verbose_name=_("Type of visit"))
    visit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Visit price"), default=0)
    visit_price_doctor = models.DecimalField(
                                            max_digits=8,
                                            decimal_places=2,
                                            verbose_name=_("Visit price for the doctor"),
                                            default=0
                                            )
    date_of_visit = models.DateField(verbose_name=_("Date of visit"))
    time_of_visit = models.TimeField(null=True, blank=True, verbose_name=_("Time of visit"))
    city = models.ForeignKey('territories.City', on_delete=models.PROTECT, verbose_name=_("City"))
    detailed_location = models.CharField(max_length=100, blank=True, verbose_name=_("Detailed location"))
    cause_of_visit = models.TextField(max_length=700, verbose_name=_("Cause of visit"))
    checkup = models.TextField(max_length=1200, verbose_name=_("Checkup"))
    additional_checkup = models.TextField(max_length=700, blank=True, verbose_name=_("Additional checkup"))
    diagnosis = models.ManyToManyField('Disease', related_name='reports', verbose_name=_("Diagnosis"))
    prescription = models.TextField(max_length=700, verbose_name=_("Prescription"))
    checked = models.BooleanField(default=False, verbose_name=_("Is checked"))
    case = models.OneToOneField(
                                'appointment_requests.InsuranceCase',
                                on_delete=models.PROTECT,
                                related_name='report',
                                verbose_name=_("Report request")
                                )

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')

    def __str__(self):
        return ' '.join((self.patients_last_name, self.patients_first_name, self.get_full_ref_number))

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Report._meta.fields]

    @property
    def get_total_price(self):
        total = 0
        if self.pk:
            services = self.service_items.get_queryset()
            for service in services:
                total += service.cost
            total += self.visit_price
            return total
        return total

    @property
    def get_total_price_doctor(self):
        total = 0
        if self.pk:
            services = self.service_items.get_queryset()
            for service in services:
                total += service.cost_doctor
            total += self.visit_price_doctor
            return total
        return total

    @property
    def get_full_ref_number(self):
        ref = (self.case.company.initials) + str(self.case.ref_number).zfill(3)
        date_of_request = str(self.case.date_time.strftime("%d%m"))
        if not self.case.doctor.is_foreign_doctor:
            info = self.case.doctor.initials + self.type_of_visit.initial
        else:
            info = self.case.doctor.initials
        return '-'.join((ref, date_of_request, info))

    @property
    def get_number_of_visit(self):
        country = self.city.district.region.country
        reports_queryset = Report.objects.filter(
            city__district__region__country=country,
            company_ref_number=self.company_ref_number,
            patients_first_name=self.patients_first_name,
            patients_last_name=self.patients_last_name
        ).order_by('date_of_visit')
        for index, item in enumerate(reports_queryset, 1):
            if self.pk == item.pk:
                return index

    @property
    def get_full_company_ref_number(self):
        number = self.get_number_of_visit
        if number > 1:
            return '_'.join((self.company_ref_number, str(number)))
        else:
            return self.company_ref_number

    get_full_ref_number.fget.short_description = _('Full ref. number')
    get_total_price.fget.short_description = _('Total price')
    get_total_price_doctor.fget.short_description = _('Total price for the doctor')


class AdditionalImage(models.Model):
    report = models.ForeignKey(
                            Report,
                            on_delete=models.CASCADE,
                            related_name='additional_images',
                            verbose_name=_("Report")
                            )
    image = models.ImageField(upload_to=get_image_path, verbose_name=_("Image"))
    position = models.IntegerField(blank=False, verbose_name=_("Position"))
    expand = models.BooleanField(default=False, verbose_name=_("Expand"))

    class Meta:
        verbose_name = _('Additional Image')
        verbose_name_plural = _('Additional Images')


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    country = models.ForeignKey(
                            'territories.Country',
                            on_delete=models.PROTECT,
                            related_name='services',
                            verbose_name=_("Country")
                            )
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))
    price_doctor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price for the doctor"))
    unsummable_price = models.BooleanField(default=False, verbose_name=_('Unsummable price'))

    class Meta:
        unique_together = (('name', 'country',),)
        verbose_name = _('Service')
        verbose_name_plural = _('Services')

    def __str__(self):
        return ' - '.join((self.country.name + ' - ' + self.name))


class ServiceItem(models.Model):
    report = models.ForeignKey(Report, related_name='service_items', on_delete=models.CASCADE, verbose_name=_("Report"))
    service = models.ForeignKey(Service, related_name='items', on_delete=models.PROTECT, verbose_name=_("Service"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_("Cost"))
    cost_doctor = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_("Cost doctor"))

    class Meta:
        unique_together = (('report', 'service',),)
        verbose_name = _('Service item')
        verbose_name_plural = _('Service items')

    def __str__(self):
        if self.quantity > 1:
            return str(self.service.name) + ' [{}]'.format(self.quantity)
        return self.service.name


@receiver(post_delete, sender=Report)
def submission_delete(sender, instance, **kwargs):
    shutil.rmtree(
                str(os.path.join(
                        settings.MEDIA_ROOT,
                        'FILES',
                        str(instance.pk)
                        )
                    ), ignore_errors=True
                )


@receiver(pre_save, sender=AdditionalImage)
def image_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_image = AdditionalImage.objects.get(pk=instance.pk).image
            os.remove(old_image.path)
        except AdditionalImage.DoesNotExist:
            pass


@receiver(post_delete, sender=AdditionalImage)
def image_delete(sender, instance, **kwargs):
    try:
        os.remove(instance.image.path)
    except OSError:
        pass


@receiver(post_delete, sender=ReportTemplate)
def template_delete(sender, instance, **kwargs):
    os.remove(instance.template.path)

