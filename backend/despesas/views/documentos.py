from django.db.models import Model
from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from despesas import serializers
from despesas.filters import TipoDocumentoFilterSet
from despesas.models import TipoDocumento, ValorDocumento, Transacao
from despesas.serializers import ValorDocumentoSerializer, TipoDocumentoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from despesas.views.ativoUtil import AtivoListDefaultMixin


class TipoDocumentoViewSet(AtivoListDefaultMixin, viewsets.ModelViewSet, ):
    queryset = TipoDocumento.objects.all()
    serializer_class = TipoDocumentoSerializer
    http_method_names  = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = TipoDocumentoFilterSet

class ValorDocumentoViewSet(viewsets.ModelViewSet):
    queryset = ValorDocumento.objects.all()
    serializer_class = ValorDocumentoSerializer
    http_method_names = ['get']


    def get_queryset(self):
        id_transacao = self.kwargs.get('transacao_pk')
        try:
            self.transacao = Transacao.objects.get(pk=id_transacao)
        except Transacao.DoesNotExist:
            raise NotFound(detail='Transação não encontrada')

        return ValorDocumento.objects.filter(versao_transacao=self.transacao.versao_transacao)

    # def retrieve(self, request, *args, **kwargs):
    #     super().get_queryset()
    #     id_tipo_documento = kwargs.get('pk')
    #     tipo_documento = ValorDocumento.objects.filter(tipo_documento=id_tipo_documento)
    #     if not tipo_documento:
    #         raise NotFound(detail='Tipo de documento não encontrado para essa transação')
    #     return Response(tipo_documento)

