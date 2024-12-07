# serializers.py
from rest_framework import serializers
from .models import Message
from .models import Tramite, Definicion,Categoria

class ChatResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user_message', 'copilot_response', 'timestamp']


# Serializador para la categoría
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['nombre']  # Solo el campo nombre de la categoría

# Serializador para los trámites
class TramiteSerializer(serializers.ModelSerializer):
    # Usamos el serializador anidado de la categoría
    categoria = CategoriaSerializer()  # Aquí incluye los detalles de la categoría

    class Meta:
        model = Tramite
        fields = '__all__'  # Incluye todos los campos del modelo Tramite

# Serializador para las definiciones
class DefinicionSerializer(serializers.ModelSerializer):
    # Usamos el serializador anidado de la categoría
    categoria = CategoriaSerializer()  # Aquí incluye los detalles de la categoría

    class Meta:
        model = Definicion
        fields = '__all__'  # Incluye todos los campos del modelo Definicion