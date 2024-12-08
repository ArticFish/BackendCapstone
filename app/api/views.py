from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Message 
import openai
from .models import Tramite,Definicion,Categoria
from .serializers import TramiteSerializer, DefinicionSerializer,CategoriaSerializer
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.http import JsonResponse
from django.db import transaction
import pandas as pd
from decouple import config
from django.contrib.auth.decorators import login_required
openai.api_key =" config('OPENAI_API_KEY')"
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from openpyxl import Workbook
from django.http import HttpResponse

openai.api_key = config('OPENAI_API_KEY')

class OpenAIMessageView(APIView):    
    def post(self, request, *args, **kwargs):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un amable asistente,el cual su objetivo principal es ayudar con temas relacionados a temas chilenos"},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150
            )
            copilot_response = response.choices[0].message['content']
            # Guardar la respuesta en la base de datos 
            chat_response = Message.objects.create( 
                user_message=user_message, 
                copilot_response=copilot_response 
            )
            
            # Serializar la respuesta 
            serializer = Message(chat_response)
            # Imprimir todos los registros en la base de datos 
            all_responses = Message.objects.all() 
            for response in all_responses: 
                print(f'User Message: {response.user_message}, Gpt Response: {response.copilot_response}, Timestamp: {response.timestamp}')
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"response": copilot_response}, status=status.HTTP_200_OK)

    def get_bot_reply(self, message):
    # Simulación de la respuesta del bot
        return f"Respuesta del bot para: {message}"

class TramiteList(APIView):
    def get(self, request):
        tramites = Tramite.objects.all()
        serializer = TramiteSerializer(tramites, many=True)
        return Response({"tramites": serializer.data}, status=status.HTTP_200_OK)

     # POST: Agregar un nuevo trámite
    def post(self, request):
        serializer = TramiteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Guarda el nuevo trámite en la base de datos
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DefinicionList(APIView):
    def get(self, request):
        definiciones = Definicion.objects.all()
        serializer = DefinicionSerializer(definiciones, many=True)
        return Response({"definiciones": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = DefinicionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Guarda la nueva definición en la base de datos
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CategoriaList(APIView):
    def get(self, request):
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)
@login_required   
def ver_definiciones(request):
    
    definiciones = Definicion.objects.all()  # Obtiene todos los datos del modelo Definicion
    print(definiciones)
    return render(request, 'verDefiniciones.html', {'definiciones': definiciones})
@login_required
def ver_guias(request):
    tramites = Tramite.objects.all()  # Obtiene todos los datos del modelo Tramite
    return render(request, 'verGuias.html', {'tramites': tramites})

# Editar y Borrar Definición
class DefinicionForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        empty_label=None,
        required=True
    )

    class Meta:
        model = Definicion
        fields = ['titulo', 'definicion', 'categoria']
@login_required
def editar_definicion(request, id):
    definicion = get_object_or_404(Definicion, pk=id)
    if request.method == 'POST':
        form = DefinicionForm(request.POST, instance=definicion)
        if form.is_valid():
            form.save()
            return redirect('verDefiniciones')  # Redirige a la lista de definiciones después de guardar
    else:
        form = DefinicionForm(instance=definicion)
    
    return render(request, 'editarDefinicion.html', {'form': form})
@login_required
def borrar_definicion(request, id):
    definicion = get_object_or_404(Definicion, pk=id)
    definicion.delete()
    return redirect('verDefiniciones')


class TramiteForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        empty_label=None,
        required=True
    )

    class Meta:
        model = Tramite
        fields = ['titulo', 'descripcion', 'tipo', 'categoria', 'requisitos', 'documentos_necesarios', 'lugar_tramite', 'plazo_estimado', 'costo', 'link_oficial']
        widgets = {
            'requisitos': forms.Textarea(attrs={'rows': 3}),
            'documentos_necesarios': forms.Textarea(attrs={'rows': 3}),
        }
@login_required
def editar_guia(request, id):
    tramite = get_object_or_404(Tramite, pk=id)
    if request.method == 'POST':
        form = TramiteForm(request.POST, instance=tramite)
        if form.is_valid():
            form.save()
            return redirect('verGuias')  # Redirige a la lista de guías después de guardar
    else:
        form = TramiteForm(instance=tramite)

    return render(request, 'editarGuia.html', {'form': form})

@login_required
def borrar_guia(request, id):
    tramite = get_object_or_404(Tramite, pk=id)
    tramite.delete()
    return redirect('verGuias')  # Redirige a la lista de guías después de borrar

@login_required
def ver_categorias(request):
    categorias = Categoria.objects.all()  # Obtener todas las categorías
    return render(request, 'verCategorias.html', {'categorias': categorias})
@login_required
def agregar_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')  # Obtener el nombre de la nueva categoría
        if nombre:
            Categoria.objects.create(nombre=nombre)  # Crear la nueva categoría
            return redirect('verCategorias')  # Redirigir a la página de ver categorías
    return render(request, 'agregarCategoria.html')
@login_required
def borrar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)  # Obtener la categoría por ID
    categoria.delete()  # Borrar la categoría
    return redirect('verCategorias')  # Redirigir a la página de ver categorías
@login_required
def subir_definiciones(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')

        if not archivo:
            return JsonResponse({"error": "No se subió ningún archivo"}, status=400)

        try:
            # Leer el archivo (puede ser CSV o Excel)
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            elif archivo.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(archivo)
            else:
                return JsonResponse({"error": "Formato de archivo no soportado. Usa CSV o Excel."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error al leer el archivo: {e}"}, status=500)

        # Validar que las columnas esperadas existan
        columnas_esperadas = ['titulo', 'definicion', 'categoria']
        if not all(col in df.columns for col in columnas_esperadas):
            return JsonResponse({"error": f"El archivo debe contener las columnas: {', '.join(columnas_esperadas)}"}, status=400)

        # Validar que no haya filas con valores faltantes
        if df[columnas_esperadas].isnull().any().any():
            return JsonResponse({"error": "No se permiten filas con valores faltantes en las columnas obligatorias."}, status=400)

        # Procesar las definiciones dentro de una transacción
        try:
            with transaction.atomic():
                for _, row in df.iterrows():
                    # Crear o recuperar la categoría
                    categoria, _ = Categoria.objects.get_or_create(nombre=row['categoria'])

                    # Crear la definición asociada
                    Definicion.objects.create(
                        titulo=row['titulo'],
                        definicion=row['definicion'],
                        categoria=categoria
                    )
        except Exception as e:
            return JsonResponse({"error": f"Error al guardar los datos: {e}"}, status=500)

        return redirect('verDefiniciones')
    return render(request, 'subirDefiniciones.html')
@login_required
def general(request):
    return render(request, 'general.html')
@login_required
def subir_guias(request):
    if request.method == "POST":
        # Validar que se haya subido un archivo
        archivo = request.FILES.get('archivo')
        if not archivo:
            return JsonResponse({"error": "No se subió ningún archivo"}, status=400)

        # Leer el archivo
        try:
            if archivo.name.endswith('.csv'):
                df = pd.read_csv(archivo)
            elif archivo.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(archivo)
            else:
                return JsonResponse({"error": "Formato de archivo no soportado"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error al procesar el archivo: {e}"}, status=500)

        # Validar las columnas esperadas
        columnas_esperadas = ['titulo', 'descripcion', 'tipo', 'categoria', 'requisitos', 'documentos_necesarios', 'lugar_tramite', 'plazo_estimado', 'costo', 'link_oficial']
        if not all(col in df.columns for col in columnas_esperadas):
            return JsonResponse({"error": f"El archivo debe contener las columnas: {', '.join(columnas_esperadas)}"}, status=400)

        # Validar que no haya filas con campos vacíos
        if df[columnas_esperadas].isnull().any().any():
            return JsonResponse({"error": "Todas las filas deben tener valores en los campos requeridos"}, status=400)

        # Procesar cada fila dentro de una transacción
        try:
            with transaction.atomic():
                for _, row in df.iterrows():
                    categoria_nombre = row['categoria']
                    categoria, _ = Categoria.objects.get_or_create(nombre=categoria_nombre)  # Crear categoría si no existe

                    Tramite.objects.create(
                        titulo=row['titulo'],
                        descripcion=row['descripcion'],
                        tipo=row['tipo'],
                        categoria=categoria,
                        requisitos=row['requisitos'],  # Asumimos que los datos son JSON
                        documentos_necesarios=row['documentos_necesarios'],  # Asumimos que los datos son JSON
                        lugar_tramite=row['lugar_tramite'],
                        plazo_estimado=row['plazo_estimado'],
                        costo=row['costo'],
                        link_oficial=row['link_oficial']
                    )
        except Exception as e:
            return JsonResponse({"error": f"Error al guardar los datos: {e}"}, status=500)

        return redirect('verGuias')  # Redirige después de agregar las guías

    return render(request, 'subirGuias.html')
@login_required
def gestionar_categorias(request):
    categorias = Categoria.objects.all()  # Obtener todas las categorías
    mensaje_error = None  # Inicializamos el mensaje de error

    # Manejo de agregar nueva categoría
    if request.method == 'POST':
        # Verificar si se está agregando o editando una categoría
        nombre = request.POST.get('nombre')

        if nombre:  # Si hay un nombre
            if 'agregar_categoria' in request.POST:  # Agregar nueva categoría
                if Categoria.objects.filter(nombre=nombre).exists():
                    mensaje_error = "La categoría ya existe."
                else:
                    Categoria.objects.create(nombre=nombre)
            elif 'editar_categoria' in request.POST:  # Editar categoría existente
                categoria_id = request.POST.get('categoria_id')
                categoria = get_object_or_404(Categoria, id=categoria_id)

                # Verificar que no se duplique el nombre de la categoría
                if Categoria.objects.filter(nombre=nombre).exclude(id=categoria.id).exists():
                    mensaje_error = "La categoría ya existe."
                else:
                    categoria.nombre = nombre
                    categoria.save()

            # Redirigir a la misma página con el mensaje de error
            return render(request, 'gestionarCategorias.html', {'categorias': categorias, 'mensaje_error': mensaje_error})

        # Borrar categoría
        if 'borrar_categoria' in request.POST:
            categoria_id = request.POST.get('categoria_id')
            categoria = get_object_or_404(Categoria, id=categoria_id)
            categoria.delete()

            # Redirigir a la misma página
            return render(request, 'gestionarCategorias.html', {'categorias': categorias, 'mensaje_error': mensaje_error})

    # Renderizar la página sin errores
    return render(request, 'gestionarCategorias.html', {'categorias': categorias, 'mensaje_error': mensaje_error})

def custom_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required
def descargar_definiciones(request):
    # Crear un archivo de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = 'Definiciones'
    
    # Escribir los encabezados de las columnas
    ws.append(['titulo', 'definicion', 'categoria'])
    
    # Obtener las definiciones de la base de datos
    definiciones = Definicion.objects.all()
    
    # Escribir las filas con las definiciones
    for definicion in definiciones:
        ws.append([definicion.titulo, definicion.definicion, definicion.categoria.nombre])
    
    # Crear una respuesta HTTP para el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="definiciones.xlsx"'
    
    # Guardar el archivo Excel en la respuesta
    wb.save(response)
    
    return response

@login_required
def descargar_tramites(request):
    # Crear un archivo de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = 'Tramites'
    
    # Escribir los encabezados de las columnas
    ws.append(['titulo','descripcion','tipo','categoria','requisitos','documentos_necesarios','lugar_tramite','plazo_estimado','costo','link_oficial'])

    # Obtener las definiciones de la base de datos
    tramites = Tramite.objects.all()
    
    # Escribir las filas con las definiciones
    for tramite in tramites:
        ws.append([tramite.titulo, tramite.descripcion,tramite.tipo, tramite.categoria.nombre,tramite.requisitos,tramite.documentos_necesarios
                   ,tramite.lugar_tramite,tramite.plazo_estimado,tramite.costo,tramite.link_oficial])
    
    # Crear una respuesta HTTP para el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tramites.xlsx"'
    
    # Guardar el archivo Excel en la respuesta
    wb.save(response)
    
    return response