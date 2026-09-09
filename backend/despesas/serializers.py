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
        fields = ["id_tipo_documento", "tipo_documento"]
        read_only_fields = ["id_tipo_documento"]


class ValorDocumentoSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)

    id_tipo_documento = serializers.PrimaryKeyRelatedField(
        queryset=TipoDocumento.objects.all(),
        source="tipo_documento",  # Aponta para o atributo do modelo Django
        write_only=True
    )

    class Meta:
        model = ValorDocumento
        fields = ["id_valor_documento", "id_tipo_documento", "tipo_documento", "valor_documento", "transacao",
                  "descricao"]
        read_only_fields = ["id_valor_documento"]

#OK
class GrupoFinalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoFinalidade
        fields = ["id_grupo_finalidade", "grupo_finalidade", "ativo"]
        read_only_fields = ["id_grupo_finalidade"]

#OK
class NaturezaFinalidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NaturezaFinalidade
        fields = ["id_natureza_finalidade", "natureza_finalidade", "ativo"]
        read_only_fields = ["id_natureza_finalidade"]

#OK
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

#OK
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
        exclude = ["id_tipo_documento","tipo_documento", "valor_documento", "versao_transacao"]
        extra_kwargs = {
            "versao_transacao": {"write_only": True}
        }


class FinalidadeField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        FinalidadeSerializer(value).data


class StatusTransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusTransacao
        fields = "__all__"


class StatusTransacaoField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return StatusTransacaoSerializer(value).data


class TransacaoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = ['id_transacao', 'data_criacao']
        read_only_fields = ['id_transacao', 'data_criacao']


class VersaoTransacaoSerializer(serializers.ModelSerializer):
    # documentos = ValorDocumentosNestedSerializer(many=True, required=False, allow_empty=True)

    # finalidade = FinalidadeSerializer(required=False, allow_null=True)
    # unidade_credora = UnidadeSerializer(required=False)
    # unidade_executora = UnidadeSerializer()
    # status_pagamento = StatusTransacao()
    # beneficiario = PessoaSerializer(required=False)
    # usuario = UserDetailsSerializer(read_only=True)

    #
    finalidade = FinalidadeField(required=False, allow_null=True, queryset=Finalidade.objects.all())
    unidade_credora = UnidadeField(required=False, allow_empty=True, queryset=Unidade.objects.all())
    unidade_executora = UnidadeField(required=True, queryset=Unidade.objects.all())
    status_pagamento = StatusTransacaoField(queryset=StatusTransacao.objects.all())
    beneficiario = PessoaField(queryset=Pessoa.objects.all(), required=False, allow_empty=True)
    usuario = UserDetailsSerializer(read_only=True)
    transacao = TransacaoReadSerializer(read_only=True)

    class Meta:
        model = VersaoTransacao
        fields = [
            "id_versao_transacao",
            "transacao",
            "numero_versao",
            "finalidade",
            "unidade_credora",
            "unidade_executora",
            "usuario",
            "status_pagamento",
            "beneficiario",
            "credito",
            "montante",
            "data_criacao",
        ]

    def validate_documentos(self, documentos):
        if self.finalidade is None:
            return documentos

        tipos_documentos = self.finalidade['tipodocumentoparafinalidade_set'].all()

        validation_errors = []

        for tipo_doc in tipos_documentos:
            if tipo_doc['obrigatorio']:
                if tipo_doc['tipo_documento']['id_tipo_documento'] not in documentos:
                    validation_errors.append(
                        f'O tipo documento {tipo_doc["tipo_documento"]["tipo_documento"]} é obrigatório.')
                    continue

        if validation_errors:
            raise serializers.ValidationError(validation_errors)

        tipos_documentos_in_finalidade = [id_doc for id_doc in tipos_documentos['tipo_documento']['id_tipo_documento']]
        for documentos_send in documentos:
            if documentos_send not in tipos_documentos_in_finalidade:
                documentos.pop(documentos_send)

        return documentos

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
