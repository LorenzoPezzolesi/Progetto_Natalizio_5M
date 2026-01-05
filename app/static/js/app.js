/**
 * Skill Tracker - Custom JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation feedback
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // XP calculator helper
    var durationInput = document.getElementById('duration_minutes');
    var xpInput = document.getElementById('xp_gained');

    if (durationInput && xpInput) {
        durationInput.addEventListener('input', function() {
            // Suggerisce XP basato sulla durata (120 XP per ora)
            var suggestedXp = this.value * 2;
            xpInput.placeholder = 'Suggerito: ' + suggestedXp + ' XP';
        });
    }
});

/**
 * Confirm delete helper function
 * Used by list templates for delete confirmation
 */
function confirmDelete(name, url, extraInfo) {
    var modalElement = document.getElementById('deleteModal');
    if (!modalElement) return;

    document.getElementById('deleteItemName').textContent = name;
    document.getElementById('deleteForm').action = url;

    var warning = document.getElementById('deleteWarning');
    if (warning && extraInfo) {
        warning.style.display = extraInfo > 0 ? 'block' : 'none';
    }

    new bootstrap.Modal(modalElement).show();
}

/**
 * Format duration from minutes to readable string
 */
function formatDuration(minutes) {
    var hours = Math.floor(minutes / 60);
    var mins = minutes % 60;

    if (hours > 0 && mins > 0) {
        return hours + 'h ' + mins + 'm';
    } else if (hours > 0) {
        return hours + 'h';
    } else {
        return mins + 'm';
    }
}
