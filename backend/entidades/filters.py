from django_filters import FilterSet, CharFilter, BooleanFilter

from entidades.models import Unidade


class UnidadeFilterSet(FilterSet):
    nome_unidade = CharFilter(field_name='nome_unidade', lookup_expr='icontains')
    cod_estruturado = CharFilter(field_name='cod_estruturado', lookup_expr='icontains')
    tipo_unidade = CharFilter(field_name='tipo_unidade', lookup_expr='icontains')
    centro = CharFilter(field_name='centro', lookup_expr='icontains')

    situacao_unidade = CharFilter(field_name='situacao_unidade', lookup_expr='icontains')

    pode_empenhar = BooleanFilter(field_name='pode_empenhar')

    class Meta:
        model = Unidade
        fields = []
