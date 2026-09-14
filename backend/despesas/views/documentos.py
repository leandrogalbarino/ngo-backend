from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from despesas.filters import TipoDocumentoFilterSet
from despesas.models import TipoDocumento, ValorDocumento
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
    http_method_names = ['get', 'patch', 'post', 'delete']

    def get_queryset(self):
        id_transacao = self.kwargs['transacao_pk']
        print(id_transacao)
        return ValorDocumento.objects.filter(versao_transacao=id_transacao)