from django_filters import BooleanFilter, CharFilter, FilterSet, NumberFilter
from entidades.models import Unidade


class UnidadeFilterSet(FilterSet):
    nome_unidade = CharFilter(field_name="nome_unidade", lookup_expr="icontains")
    cod_estruturado = CharFilter(field_name="cod_estruturado", lookup_expr="icontains")
    nome_centro = CharFilter(field_name="centro__nome_centro", lookup_expr="icontains")

    id_centro = NumberFilter(field_name="centro__id_centro_interno")
    id_tipo_unidade = NumberFilter(field_name="centro__id_tipo_unidade")
    id_situacao_unidade = NumberFilter(
        field_name="situacao_unidade__id_situacao_unidade"
    )

    tipo_unidade = CharFilter(
        field_name="tipo_unidade__tipo_unidade", lookup_expr="icontains"
    )
    situacao_unidade = CharFilter(
        field_name="situacao_unidade__situacao_unidade", lookup_expr="icontains"
    )

    pode_empenhar = BooleanFilter(field_name="pode_empenhar")

    class Meta:
        model = Unidade
        fields = []
