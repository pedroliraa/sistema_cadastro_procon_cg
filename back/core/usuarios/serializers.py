from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .permissions import ANALISTA, GESTOR


class UsuarioSerializer(serializers.ModelSerializer):
    perfil = serializers.ChoiceField(choices=[ANALISTA, GESTOR], write_only=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name",
                  "password", "perfil", "is_active"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        grupo = instance.groups.first()
        data["perfil"] = grupo.name if grupo else None
        return data

    def create(self, validated_data):
        perfil = validated_data.pop("perfil")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.groups.set([Group.objects.get(name=perfil)])
        return user

    def update(self, instance, validated_data):
        perfil = validated_data.pop("perfil", None)
        password = validated_data.pop("password", None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        if password:
            instance.set_password(password)
        instance.save()
        if perfil:
            instance.groups.set([Group.objects.get(name=perfil)])
        return instance