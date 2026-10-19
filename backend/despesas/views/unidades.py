from despesas.serializers import (
    UnidadeSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend
from entidades.filters import UnidadeFilterSet
from entidades.models import Unidade
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter


class UnidadeViewSet(viewsets.ModelViewSet):
    queryset = Unidade.objects.all().select_related(
        "centro", "tipo_unidade", "situacao_unidade"
    )
    http_method_names = ["get"]

    ordering_fields = ["tipo_unidade"]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    serializer_class = UnidadeSerializer
    filterset_class = UnidadeFilterSet
