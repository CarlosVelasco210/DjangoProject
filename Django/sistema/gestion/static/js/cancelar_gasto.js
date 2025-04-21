$(document).on('click', '.btn-cancelar', function() {
    const id = $(this).data('id');
    const descripcion = $(this).data('descripcion');
    $('#modalDescripcion').text(descripcion);
    $('#cancelarGastoForm').attr('action', `/cancelar_gasto/${id}/`);
});