from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from despesas.filters import FinalidadeFilterSet, GrupoFinalidadeFilterSet, NaturezaFinalidadeFilterSet
from despesas.models import NaturezaFinalidade, GrupoFinalidade, Finalidade
from despesas.serializers import NaturezaFinalidadeSerializer, FinalidadeSerializer, GrupoFinalidadeSerializer


class NaturezaFinalidadeViewSet(ModelViewSet):
    queryset = NaturezaFinalidade.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    ordering_fields = ['id_natureza_finalidade','natureza_finalidade']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    serializer_class = NaturezaFinalidadeSerializer
    filterset_class = NaturezaFinalidadeFilterSet

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()


class GrupoFinalidadeViewSet(ModelViewSet):
    queryset = GrupoFinalidade.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    ordering_fields = ['id_grupo_finalidade','grupo_finalidade']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    serializer_class = GrupoFinalidadeSerializer
    filterset_class = GrupoFinalidadeFilterSet

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()


class FinalidadeViewSet(ModelViewSet):
    queryset = Finalidade.objects.all().select_related("natureza_finalidade", "grupo_finalidade").prefetch_related(
        "tipodocumentoparafinalidade_set")
    http_method_names = ['get', 'post', 'patch', 'delete']
    ordering_fields = ['id_finalidade', 'finalidade']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    serializer_class = FinalidadeSerializer
    filterset_class = FinalidadeFilterSet

    def perform_destroy(self, instance):
        instance.ativo = False
        instance.save()
