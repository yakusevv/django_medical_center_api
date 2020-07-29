from rest_framework import viewsets
from rest_framework import permissions
import django_filters.rest_framework

from .models import Country, Region, District, City
from .serializers import CountrySerializer, RegionSerializer, DistrictSerializer, CitySerializer


class CountryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class RegionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    serializer_class = RegionSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        queryset = Region.objects.all()
        if not self.request.user.is_staff:
            country = self.request.user.profile.city.district.region.country
            queryset = queryset.filter(country=country)
        return queryset


class DistrictViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    serializer_class = DistrictSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        queryset = District.objects.all()
        if not self.request.user.is_staff:
            country = self.request.user.profile.city.district.region.country
            queryset = queryset.filter(region__country=country)
        return queryset


class CityViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissions]
    serializer_class = CitySerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def get_queryset(self):
        queryset = City.objects.all()
        if not self.request.user.is_staff:
            country = self.request.user.profile.city.district.region.country
            queryset = queryset.filter(district__region__country=country)
        return queryset
