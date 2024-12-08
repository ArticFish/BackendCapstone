from django.urls import path
from .views import OpenAIMessageView
from . import views

from django.contrib.auth.views import LoginView, LogoutView
urlpatterns = [
    path('openai/chat/', OpenAIMessageView.as_view(), name='openai-chat'),
    path('tramites/', views.TramiteList.as_view(), name='tramite-list'),
    path('definiciones/', views.DefinicionList.as_view(), name='definicion-list'),
    path('categorias/', views.CategoriaList.as_view(), name='categorias-list'),

    path('general/', views.general, name='general'),

    path('verDefiniciones/', views.ver_definiciones, name='verDefiniciones'),
    path('verDefiniciones/editar/<int:id>/', views.editar_definicion, name='editarDefinicion'),
    path('verDefiniciones/borrar/<int:id>/', views.borrar_definicion, name='borrarDefinicion'),
    path('subirDefiniciones/', views.subir_definiciones, name='subirDefiniciones'),
    path('descargarDefiniciones/', views.descargar_definiciones, name='descargarDefiniciones'),

    path('verGuias/', views.ver_guias, name='verGuias'),
    path('editar-guia/<int:id>/', views.editar_guia, name='editarGuia'),
    path('borrar-guia/<int:id>/', views.borrar_guia, name='borrarGuia'),
    path('subir-guias/', views.subir_guias, name='subirGuias'),
    path('descargarGuias/', views.descargar_tramites, name='descargarGuias'),
    path('gestionar-categorias/', views.gestionar_categorias, name='gestionarCategorias'),
    
    path('', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
]