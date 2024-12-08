from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
class Message(models.Model):
    user_message = models.TextField() 
    copilot_response = models.TextField() 
    timestamp = models.DateTimeField(auto_now_add=True)

    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre de la categoría

    def __str__(self):
        return self.nombre
    
class Tramite(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    requisitos = models.JSONField()
    documentos_necesarios = models.JSONField()
    lugar_tramite = models.CharField(max_length=255)
    plazo_estimado = models.CharField(max_length=200)
    costo = models.CharField(max_length=200)
    link_oficial = models.CharField(max_length=200)

    
    def __str__(self):
        return self.titulo


class Definicion(models.Model):
    titulo = models.CharField(max_length=255)
    definicion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo
    
