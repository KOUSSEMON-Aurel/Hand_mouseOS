/**
 * Logique simple pour simuler ou recevoir des données de HandMouseOS
 * en TypeScript (pour les stats GitHub).
 */

interface SystemStats {
    cpu: number;
    fps: number;
    gesture: string;
    action: string;
}

class DashboardManager {
    private cpuEl: HTMLElement | null;
    private fpsEl: HTMLElement | null;
    private gestureEl: HTMLElement | null;
    private actionEl: HTMLElement | null;

    constructor() {
        this.cpuEl = document.getElementById('cpu-value');
        this.fpsEl = document.getElementById('fps-value');
        this.gestureEl = document.getElementById('gesture-value');
        this.actionEl = document.getElementById('gesture-action');
    }

    public updateStats(stats: SystemStats) {
        if (this.cpuEl) this.cpuEl.innerText = `${stats.cpu}%`;
        if (this.fpsEl) this.fpsEl.innerText = `${stats.fps}`;
        if (this.gestureEl) this.gestureEl.innerText = stats.gesture;
        if (this.actionEl) this.actionEl.innerText = stats.action;

        console.log(`[Dashboard] Stats updated: ${stats.gesture}`);
    }

    public addLog(message: string, type: 'info' | 'warn' | 'error' = 'info') {
        const logsContainer = document.getElementById('logs');
        if (logsContainer) {
            const entry = document.createElement('p');
            entry.className = `log-entry ${type}`;
            entry.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
            logsContainer.prepend(entry);
        }
    }
}

// Initialisation au chargement
window.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardManager();

    // Simulation d'activité
    setTimeout(() => {
        dashboard.updateStats({
            cpu: 12,
            fps: 60,
            gesture: 'Index_Pinch',
            action: 'Left_Click'
        });
        dashboard.addLog("Geste détecté: Index_Pinch");
    }, 2000);
});
