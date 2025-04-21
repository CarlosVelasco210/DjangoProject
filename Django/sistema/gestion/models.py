from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    usuario = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=100)
    rol = models.CharField(max_length=50)

    def __str__(self):
        fila = "usuario: " + self.usuario + " - " + "Contraseña: " + self.contrasena + " - " + "Rol: " + self.rol
        return fila

class TipoGasto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Gasto(models.Model):
    descripcion = models.TextField()
    monto = models.IntegerField()
    fecha_registro = models.DateField(editable=False)
    fecha_limite = models.DateField()
    estado = models.CharField(max_length=50)
    motivo_cancelacion = models.TextField(null=True, blank=True)
    tipo_gasto = models.ForeignKey(TipoGasto, on_delete=models.CASCADE, verbose_name="TipoGasto")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.descripcion

class Pago(models.Model):
    gasto = models.ForeignKey(Gasto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Pago relacionado con {self.gasto.descripcion}"

class CuentaBancaria(models.Model):
    num_cuenta = models.BigIntegerField()
    banco = models.CharField(max_length=100)
    saldo = models.IntegerField()

    def __str__(self):
        return f"Cuenta de {self.banco} - {self.num_cuenta}"

class DetallePago(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    monto_pagado = models.IntegerField()
    fecha_pago = models.DateField()
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE)

    def __str__(self):
        return f"Detalle de pago {self.pago.id} - {self.monto_pagado}"
