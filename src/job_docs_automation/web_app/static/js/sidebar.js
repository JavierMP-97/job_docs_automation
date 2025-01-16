document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const toggleButton = document.getElementById('sidebar-toggle');
    const overlay = document.createElement('div');
    overlay.classList.add('overlay');
    document.body.appendChild(overlay);

    const toggleSidebar = () => {
        sidebar.classList.toggle('open');
        if (window.innerWidth <= 768) {
            if (sidebar.classList.contains('open')) {
                overlay.classList.add('active');
            }
            else {
                overlay.classList.remove('active');
            }
        }
    };

    toggleButton.addEventListener('click', toggleSidebar);

    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth <= 768) {
            if (sidebar.classList.contains('open')) {
                overlay.classList.add('active');
            }
            else {
                overlay.classList.remove('active');
            }
        } else {
            overlay.classList.remove('active');
        }
    });
});