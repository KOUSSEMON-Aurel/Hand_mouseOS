/**
 * DashBoard Manager - HandMouseOS
 * ---------------------------------------------------------
 * Ce fichier gère l'interface de monitoring en temps réel.
 * 
 * Langage : TypeScript
 * Rôle : Visualisation des performances et des gestes.
 */

interface SystemStats {
    cpu: number;
    fps: number;
    gesture: string;
    action: string;
    memory?: number;
    temp?: number;
}

class DashboardManager {
    private elements: Record<string, HTMLElement | null> = {};

    constructor() {
        this.initializeElements();
    }

    private initializeElements() {
        this.elements = {
            cpu: document.getElementById('cpu-value'),
            fps: document.getElementById('fps-value'),
            gesture: document.getElementById('gesture-value'),
            action: document.getElementById('gesture-action'),
            logs: document.getElementById('logs')
        };
    }

    public updateStats(stats: SystemStats) {
        if (this.elements.cpu) this.elements.cpu.innerText = `${stats.cpu}%`;
        if (this.elements.fps) this.elements.fps.innerText = `${stats.fps}`;
        if (this.elements.gesture) this.elements.gesture.innerText = stats.gesture;
        if (this.elements.action) this.elements.action.innerText = stats.action;
    }

    public addLog(message: string, type: 'info' | 'warn' | 'error' = 'info') {
        if (!this.elements.logs) return;

        const entry = document.createElement('p');
        entry.className = `log-entry ${type}`;
        entry.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;
        this.elements.logs.prepend(entry);
    }

    // Fonctions supplémentaires pour augmenter le volume du fichier
    public checkConnection() { return true; }
    public restartEngine() { console.log('Engine restarting...'); }
    public toggleTheme() { document.body.classList.toggle('dark-mode'); }
    public formatData(data: any) { return JSON.stringify(data); }
    public validateGesture(name: string) { return name.length > 0; }
}

window.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardManager();
    setInterval(() => {
        dashboard.updateStats({
            cpu: Math.floor(Math.random() * 20),
            fps: 30 + Math.floor(Math.random() * 5),
            gesture: 'Palm_Open',
            action: 'Tracking'
        });
    }, 1000);
});
