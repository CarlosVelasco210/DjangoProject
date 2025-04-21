document.addEventListener('DOMContentLoaded', function () {
    const tooltips = document.querySelectorAll('span[title]');
    tooltips.forEach(function (tooltip) {
        tooltip.addEventListener('mouseenter', function () {
            const tooltipBox = document.createElement('div');
            tooltipBox.className = 'custom-tooltip';
            tooltipBox.textContent = tooltip.getAttribute('title');
            document.body.appendChild(tooltipBox);

            const rect = tooltip.getBoundingClientRect();
            tooltipBox.style.left = rect.left + window.scrollX + 'px';
            tooltipBox.style.top = rect.top + window.scrollY - tooltipBox.offsetHeight - 5 + 'px';

            tooltip.addEventListener('mouseleave', function () {
                tooltipBox.remove();
            });
        });
    });
});