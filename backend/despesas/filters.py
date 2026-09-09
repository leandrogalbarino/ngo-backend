from django_filters import FilterSet, CharFilter

from despesas.models import Finalidade, GrupoFinalidade, NaturezaFinalidade


def filter_ativo(queryset, name, value):
    if value == 'all':
        return queryset
    elif value == 'false':
        return queryset.filter(ativo=False)
    return queryset.filter(ativo=True)


class FinalidadeFilterSet(FilterSet):
    ativo = CharFilter(method='filter_ativo')
    finalidade = CharFilter(field_name='finalidade', lookup_expr='icontains')
    grupo_finalidade = CharFilter(field_name='grupo_finalidade__grupo_finalidade', lookup_expr='icontains')
    natureza_finalidade = CharFilter(field_name='natureza_finalidade__natureza_finalidade', lookup_expr='icontains')

    class Meta:
        model = Finalidade
        fields = []


class GrupoFinalidadeFilterSet(FilterSet):
    ativo = CharFilter(method='filter_ativo')
    grupo_finalidade = CharFilter(field_name='grupo_finalidade', lookup_expr='icontains')

    class Meta:
        model = GrupoFinalidade
        fields = []


class NaturezaFinalidadeFilterSet(FilterSet):
    ativo = CharFilter(method='filter_ativo')
    natureza_finalidade = CharFilter(field_name='natureza_finalidade', lookup_expr='icontains')

    class Meta:
        model = NaturezaFinalidade
        fields = []
