$(document).on('click', '.btn-cancelar-pago', function () {
    const pagoId = $(this).data('id');
    const descripcion = $(this).data('descripcion');

    $('#modalDescripcion').text(descripcion);
    $('#cancelarPagoForm').attr('action', `/cancelar_pago/${pagoId}/`);

    $('#cancelarModal').modal('show');
});
