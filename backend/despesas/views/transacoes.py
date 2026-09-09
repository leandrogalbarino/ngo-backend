from rest_framework import viewsets
from despesas.models import Transacao, StatusTransacao
from despesas.serializers import TransacaoSerializer, StatusTransacaoSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

class TransacoesViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    http_method_names = ['get', 'post', 'patch']

    ordering_fields = ['id_transacao', 'data_criacao']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    serializer_class = TransacaoSerializer
    filterset_fields = ['data_criacao']


class StatusTransacaoViewSet(viewsets.ModelViewSet):
    queryset = StatusTransacao.objects.all()
    serializer_class = StatusTransacaoSerializer
    http_method_names = ['get']
