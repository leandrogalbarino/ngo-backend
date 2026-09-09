from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from despesas.models import *
from entidades.serializers import UnidadeField, PessoaField
from usuarios.serializers import UserDetailsSerializer


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ["id_tipo_documento", "tipo_documento", "ativo"]
        read_only_fields = ["id_tipo_documento"]


class ValorDocumentoSerializer(serializers.ModelSerializer):
    id_tipo_documento = serializers.PrimaryKeyRelatedField(
        queryset=TipoDocumento.objects.all(),
        source="tipo_documento"
    )
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    #id_versao_transacao = serializers.PrimaryKeyRelatedField(queryset=VersaoTransacao.objects.all(),
     #                                                        source="versao_transacao")

    class Meta:
        model = ValorDocumento
        fields = ["id_tipo_documento", "valor_documento", "tipo_documento"]



class GrupoFinalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoFinalidade
        fields = ["id_grupo_finalidade", "grupo_finalidade", "ativo"]
        read_only_fields = ["id_grupo_finalidade"]


class NaturezaFinalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NaturezaFinalidade
        fields = ["id_natureza_finalidade", "natureza_finalidade", "ativo"]
        read_only_fields = ["id_natureza_finalidade"]


class TipoDocumentoParaFinalidadeSerializer(serializers.ModelSerializer):
    tipo_documento = serializers.StringRelatedField(read_only=True)
    id_tipo_documento = PrimaryKeyRelatedField(queryset=TipoDocumento.objects.all(), source="tipo_documento")

    class Meta:
        model = TipoDocumentoParaFinalidade
        fields = ["id_tipo_documento", "tipo_documento", "obrigatorio"]

    def validate_id_tipo_documento(self, value):
        if not value.ativo:
            raise serializers.ValidationError(
                f"O tipo de documento '{value}' não está ativo(a)."
            )
        return value


class FinalidadeSerializer(serializers.ModelSerializer):
    id_natureza_finalidade = PrimaryKeyRelatedField(queryset=NaturezaFinalidade.objects.all(), write_only=True,
                                                    source="natureza_finalidade")
    id_grupo_finalidade = PrimaryKeyRelatedField(queryset=GrupoFinalidade.objects.all(), write_only=True,
                                                 source="grupo_finalidade")
    natureza_finalidade = serializers.StringRelatedField(read_only=True)
    grupo_finalidade = serializers.StringRelatedField(read_only=True)

    tipos_documentos = TipoDocumentoParaFinalidadeSerializer(
        source="tipodocumentoparafinalidade_set", many=True)

    class Meta:
        model = Finalidade
        fields = [
            "id_finalidade",
            "natureza_finalidade",
            "grupo_finalidade",
            "id_natureza_finalidade",
            "id_grupo_finalidade",
            "finalidade",
            "tipos_documentos",
            "ativo"
        ]

        read_only_fields = ["id_finalidade"]

    def validate_id_natureza_finalidade(self, natureza):
        if not natureza.ativo:
            raise serializers.ValidationError(f"A natureza de finalidade '{natureza}' não está ativo(a).")
        return natureza

    def validate_id_grupo_finalidade(self, grupo):
        if not grupo.ativo:
            raise serializers.ValidationError(f"A natureza de finalidade '{grupo}' não está ativo(a).")
        return grupo

    def create(self, validated_data):
        tipos_documentos = validated_data.pop("tipodocumentoparafinalidade_set", [])
        with transaction.atomic():
            finalidade = Finalidade.objects.create(**validated_data)
            relations = [
                TipoDocumentoParaFinalidade(
                    finalidade=finalidade,
                    tipo_documento=item['tipo_documento'],
                    obrigatorio=item.get("obrigatorio", True)
                )
                for item in tipos_documentos
            ]

            if len(relations) > 0:
                TipoDocumentoParaFinalidade.objects.bulk_create(relations)

        return finalidade

    def update(self, instance, validated_data):
        tipos_documentos = validated_data.pop("tipodocumentoparafinalidade_set", [])
        instance = super().update(instance, validated_data)

        tipos_documentos = [i for i in tipos_documentos if 'tipo_documento' in i]

        for item in tipos_documentos:
            item_registered = False
            for tipo_registered in instance.tipodocumentoparafinalidade_set.all():
                if item['tipo_documento'].pk == tipo_registered.tipo_documento.id_tipo_documento:
                    tipo_registered.obrigatorio = item.get('obrigatorio', True)
                    tipo_registered.save()
                    item_registered = True
                    break
            if not item_registered:
                TipoDocumentoParaFinalidade.objects.create(
                    finalidade=instance,
                    tipo_documento=item['tipo_documento'],
                    obrigatorio=item.get('obrigatorio', True)
                )
        return instance


# OK
class ValorDocumentosNestedSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    id_documento = PrimaryKeyRelatedField(queryset=TipoDocumento.objects.all(), source="tipo_documento")

    class Meta:
        model = ValorDocumento
        exclude = ["id_tipo_documento", "tipo_documento", "valor_documento", "versao_transacao"]
        extra_kwargs = {
            "versao_transacao": {"write_only": True}
        }

class StatusTransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusTransacao
        fields = "__all__"


class TransacaoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = ['id_transacao', 'data_criacao']
        read_only_fields = ['id_transacao', 'data_criacao']


class VersaoTransacaoSerializer(serializers.ModelSerializer):
    id_finalidade = PrimaryKeyRelatedField(required=False, allow_null=True, queryset=Finalidade.objects.all(),
                                           source="finalidade")
    id_unidade_credora = serializers.PrimaryKeyRelatedField(queryset=Unidade.objects.all(), required=False,
                                                            allow_null=True, source="unidade_credora")
    id_unidade_executora = serializers.PrimaryKeyRelatedField(queryset=Unidade.objects.all(),
                                                              source="unidade_executora")
    id_status_pagamento = serializers.PrimaryKeyRelatedField(queryset=StatusTransacao.objects.all(),
                                                             source="status_pagamento")
    id_beneficiario = serializers.PrimaryKeyRelatedField(required=False, allow_null=True, queryset=Pessoa.objects.all(),
                                                         source="beneficiario")
    id_usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    finalidade = serializers.StringRelatedField(read_only=True)
    unidade_credora = serializers.StringRelatedField(read_only=True)
    unidade_executora = serializers.StringRelatedField(read_only=True)
    status_pagamento = serializers.StringRelatedField(read_only=True)
    beneficiario = serializers.StringRelatedField(read_only=True)
    usuario = serializers.StringRelatedField(read_only=True)

    id_transacao = serializers.PrimaryKeyRelatedField(read_only=True, source="transacao")

    documentos = ValorDocumentoSerializer(many=True, required=False, default=[])

    class Meta:
        model = VersaoTransacao
        fields = [
            "id_versao_transacao",
            "id_transacao",
            "numero_versao",

            "id_finalidade",
            "finalidade",

            "id_unidade_credora",
            "unidade_credora",

            "id_unidade_executora",
            "unidade_executora",

            "id_usuario",
            "usuario",

            "id_status_pagamento",
            "status_pagamento",

            "id_beneficiario",
            "beneficiario",

            "documentos",
            "credito",
            "montante",
            "data_criacao",
        ]

    def validate(self, data):
        finalidade = data.get('finalidade')
        documentos = data.get('documentos')

        if not finalidade:
            return data

        tipos_documentos_possiveis = finalidade.tipodocumentoparafinalidade_set.all()

        validation_errors = []
        documentos_id = [doc['tipo_documento'].pk for doc in documentos]

        for tipo_doc in tipos_documentos_possiveis:
            if tipo_doc.obrigatorio:
                if tipo_doc.tipo_documento.tipo_documento not in documentos_id:
                    raise serializers.ValidationError({'documentos': f'{tipo_doc.tipo_documento.id_tipo_documento} documentos: {documentos_id}'})
                    validation_errors.append(
                        f'O tipo documento {tipo_doc.tipo_documento.tipo_documento} é obrigatório.')
                    continue

        if validation_errors:
            raise serializers.ValidationError({'documentos': validation_errors})

        tipos_documentos_in_finalidade = [id_doc for id_doc in
                                          tipos_documentos_possiveis.tipo_documento.id_tipo_documento]
        for documentos_send in documentos:
            if documentos_send not in tipos_documentos_in_finalidade:
                documentos.pop(documentos_send)

        data['finalidade'] = finalidade
        data['documentos'] = documentos
        return data

    def create(self, validated_data):
        documentos_data = validated_data.pop("documentos", [])
        user = self.context['request'].user

        versao_transacao = None
        with transaction.atomic():
            versao_transacao = VersaoTransacao.objects.create(**validated_data)
            docs = [
                ValorDocumento(versao_transacao=versao_transacao, usuario=user, **doc) for doc in documentos_data
            ]
            ValorDocumento.objects.bulk_create(docs)
        if versao_transacao is None:
            raise ValidationError(f"Erro ao criar transacao {versao_transacao}")

        return versao_transacao

    # def validate(self, data):
    #     empenho = data.get("empenho")
    #     montante = data.get("montante")
    #     id_transacao = data.get("id_transacao")
    #     eh_credito = data.get("eh_credito")
    #
    #     if empenho and not empenho.ativo:
    #         raise serializers.ValidationError(
    #             {"empenho": "Não é possível criar ou modificar transações de um empenho inativo."}
    #         )
    #
    #     queryset = Transacao.objects.filter(empenho=empenho)
    #     if self.instance:
    #         queryset = queryset.exclude(id_transacao=id_transacao)
    #
    #     total_despesas = (
    #             queryset.aggregate(
    #                 total=Sum(
    #                     Case(
    #                         When(eh_credito=True, then=F("montante")),
    #                         When(eh_credito=False, then=-F("montante")),
    #                     )
    #                 )
    #             )["total"]
    #             or 0.00
    #     )
    #
    #     if not eh_credito and montante > total_despesas:
    #         raise serializers.ValidationError(
    #             {
    #                 "montante": f"Saldo insuficiente. O Valor da despesa (R$ {montante:.2f}) é maior que o saldo atual (R$ {total_despesas:.2f})."}
    #         )
    #     return data


class TransacaoSerializer(serializers.ModelSerializer):
    transacao = VersaoTransacaoSerializer(required=True, allow_null=False, source="versao_transacao")

    class Meta:
        model = Transacao
        fields = ['id_transacao', 'transacao', 'data_criacao']
        read_only_fields = ['id_transacao', 'data_criacao']

    def create(self, validated_data):
        versao_transacao_data = validated_data.pop('versao_transacao', None)
        user = self.context['request'].user

        with transaction.atomic():
            transacao = Transacao.objects.create(**validated_data)
            versao_transacao_data['transacao'] = transacao
            versao_transacao_data['usuario'] = user
            if versao_transacao_data is not None:
                versao_transacao_instance = VersaoTransacao.objects.create(**versao_transacao_data)
                transacao.versao_transacao = versao_transacao_instance
                transacao.save()

        return transacao

# class EmpenhoSerializer(serializers.ModelSerializer):
#     transacoes = TransacaoSerializer(many=True, read_only=True)
#     montante = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Empenho
#         fields = ["id_empenho", "numero_empenho", "numero_pen", "descricao", "finalidade", "montante", "transacoes"]
#         read_only_fields = ["id_empenho"]
#
#     def get_montante(self, obj):
#         valor_somado = (
#                 Transacao.objects.filter(empenho=obj).aggregate(
#                     total=Sum(
#                         Case(
#                             When(eh_credito=True, then=F("montante")),
#                             When(eh_credito=False, then=-F("montante")),
#                         )
#                     )
#                 )["total"]
#                 or 0.00
#         )
#
#         return valor_somado
#
# class StatusTransacaoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StatusTransacao
#         fields = "__all__"
