const form = document.querySelector('form');
const modal = document.getElementById('confirmModal');
const confirmBtn = document.getElementById('confirmBtn');
const cancelBtn = document.getElementById('cancelBtn');
const closeBtn = document.querySelector('.close');

form.addEventListener('submit', function (event) {
    event.preventDefault();
    modal.style.display = 'flex';
});

confirmBtn.addEventListener('click', function () {
    modal.style.display = 'none'; 
    form.submit();
});

cancelBtn.addEventListener('click', function () {
    modal.style.display = 'none';
});

closeBtn.addEventListener('click', function () {
    modal.style.display = 'none';
});

window.addEventListener('click', function (event) {
    if (event.target === modal) {
        modal.style.display = 'none'; 
    }
});
