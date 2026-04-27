// Main JavaScript - Digital Quiz Tool

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flash messages
    setTimeout(() => {
        const container = document.getElementById('flashContainer');
        if (container) {
            container.style.transition = 'opacity 0.5s';
            container.style.opacity = '0';
            setTimeout(() => container.remove(), 500);
        }
    }, 5000);

    // Mobile sidebar toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('open');
        });

        if (overlay) {
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('open');
                overlay.classList.remove('open');
            });
        }
    }

    // Search functionality
    const searchInput = document.getElementById('examSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.exam-card');
            cards.forEach(card => {
                const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
                const dept = card.querySelector('.exam-card-badge')?.textContent.toLowerCase() || '';
                const visible = title.includes(query) || dept.includes(query);
                card.style.display = visible ? '' : 'none';
            });
        });
    }

    // Department filter buttons
    const filterBtns = document.querySelectorAll('[data-filter]');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const dept = btn.dataset.filter.toLowerCase();
            const cards = document.querySelectorAll('.exam-card');

            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            cards.forEach(card => {
                if (dept === 'all') {
                    card.style.display = '';
                } else {
                    const cardDept = card.querySelector('.exam-card-badge')?.textContent.toLowerCase() || '';
                    card.style.display = cardDept.includes(dept) ? '' : 'none';
                }
            });
        });
    });

    // Confirmation dialogs
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (!confirm(btn.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});

// Modal helpers
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}
