from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('pagos/', views.pagos_dashboard, name='pagos_dashboard'),
    path('gastos/', views.gastos_dashboard, name='gastos_dashboard'),
    path('gastos/crear_gasto', views.crear_gasto, name='crear_gasto'),
    path('cancelar_gasto/<int:gasto_id>/', views.cancelar_gasto, name='cancelar_gasto'),
    path('pagos/validar/<int:pago_id>/', views.validar_pago, name='validar_pago'),
    path('pagos/rechazar/<int:pago_id>/', views.rechazar_pago, name='rechazar_pago'),
    path('cancelar_pago/<int:pago_id>/', views.cancelar_pago, name='cancelar_pago'),
    path('pagar_multiple/', views.pagar_multiple, name='pagar_multiple'),
    path('pagos/mostrar_detalle_pagos/', views.mostrar_detalle_pagos, name='mostrar_detalle_pagos'),

]