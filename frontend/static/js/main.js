// NetPulse AI - Core Telemetry & UI Engine JavaScript

window.NetSage = {
    // Cyber Toast notifications
    toast(message, type = 'success') {
        const container = this.getToastContainer();
        const toast = document.createElement('div');
        const bgClass = type === 'error' ? 'bg-danger text-white' : type === 'warning' ? 'bg-warning text-dark' : 'bg-success text-white';
        toast.className = `toast align-items-center ${bgClass} border-0 shadow-lg`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex align-items-center p-2">
                <div class="toast-body font-monospace small"><i class="bi bi-info-circle me-2"></i>${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        container.appendChild(toast);
        new bootstrap.Toast(toast, { delay: 3500 }).show();
    },

    getToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1090';
            document.body.appendChild(container);
        }
        return container;
    },

    // Loading state helper
    setLoading(element, loading = true) {
        if (loading) {
            element.classList.add('disabled');
            element.disabled = true;
        } else {
            element.classList.remove('disabled');
            element.disabled = false;
        }
    },

    // API fetch helper
    async api(endpoint, options = {}) {
        const defaultOptions = {
            headers: { 'Content-Type': 'application/json' }
        };
        const response = await fetch(endpoint, { ...defaultOptions, ...options });
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        return response.json();
    },

    // Formatters
    formatConfidence(confidence) {
        return (confidence * 100).toFixed(0) + '%';
    },

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Clipboard copy tool
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.toast('Telemetry copied to clipboard');
        } catch (e) {
            this.toast('Failed to copy text', 'error');
        }
    },

    // Download text helper
    downloadText(text, filename = 'telemetry_export.txt') {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        this.toast(`Exported file: ${filename}`);
    }
};

// Aliases for backwards compatibility
window.NetPulse = window.NetSage;

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    // Keyboard shortcuts: Ctrl/Cmd + Enter to submit active forms
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement?.closest('form');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.click();
            }
        }
    });
});