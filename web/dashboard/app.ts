/**
 * ============================================================================
 * HANDMOUSE OS - DASHBOARD UI MANAGER (TypeScript)
 * ============================================================================
 * 
 * Ce composant gère l'interface de visualisation web en temps réel pour
 * le projet HandMouseOS. Il permet de monitorer l'état du moteur de
 * tracking, les gestes détectés et l'utilisation des ressources système.
 * 
 * FONCTIONNALITÉS :
 * 1. Interface de monitoring temps réel (WebSockets / Polling)
 * 2. Visualisation des gestes (Pinch, Palm, Fist, etc.)
 * 3. Log console pour le moteur Rust et Python
 * 4. Graphiques de charge CPU et FPS
 * 
 * DÉTAILS TECHNIQUES :
 * Ce fichier est écrit en TypeScript pour garantir une sécurité de typage
 * lors des échanges de données entre le backend (Python/Rust) et 
 * l'interface utilisateur.
 * 
 * ----------------------------------------------------------------------------
 * COMPOSANTS DE L'INTERFACE :
 * - Stats Grid: Contient les jauges de performance.
 * - Log Console: Affiche les événements système chronologiquement.
 * - Feedback Overlay: Affiche les noms des gestes par-dessus la vue.
 * ----------------------------------------------------------------------------
 * 
 * @module Dashboard
 * @version 1.0.0
 * @author Aurel
 * ============================================================================
 */

interface SystemStats {
    cpu: number;
    fps: number;
    gesture: string;
    action: string;
    memory?: number;
    temp?: number;
    uptime?: number;
}

/**
 * Classe principale gérant la mise à jour du DOM
 */
class DashboardManager {
    private elements: Record<string, HTMLElement | null> = {};
    private isConnected: boolean = false;

    constructor() {
        console.log("Démarrage du Dashboard Manager TypeScript...");
        this.initializeElements();
        this.setupEventListeners();
    }

    private initializeElements() {
        this.elements = {
            cpu: document.getElementById('cpu-value'),
            fps: document.getElementById('fps-value'),
            gesture: document.getElementById('gesture-value'),
            action: document.getElementById('gesture-action'),
            logs: document.getElementById('logs'),
            container: document.querySelector('.glass-container')
        };
    }

    private setupEventListeners() {
        // Simulation d'événements futurs
        window.addEventListener('resize', () => this.handleResize());
    }

    /**
     * @method updateStats
     * Met à jour les éléments visuels avec les données du moteur
     */
    public updateStats(stats: SystemStats) {
        if (this.elements.cpu) {
            this.elements.cpu.innerText = `${stats.cpu}%`;
            const fill = document.querySelector('.fill') as HTMLElement;
            if (fill) fill.style.width = `${stats.cpu}%`;
        }

        if (this.elements.fps) this.elements.fps.innerText = `${stats.fps}`;
        if (this.elements.gesture) this.elements.gesture.innerText = stats.gesture;
        if (this.elements.action) this.elements.action.innerText = stats.action;
    }

    /**
     * @method addLog
     * Ajoute une entrée dans la console système
     */
    public addLog(message: string, type: 'info' | 'warn' | 'error' = 'info') {
        if (!this.elements.logs) return;

        const entry = document.createElement('p');
        entry.className = `log-entry ${type}`;
        const time = new Date().toLocaleTimeString();
        entry.innerHTML = `<span class="time">[${time}]</span> ${message}`;
        this.elements.logs.prepend(entry);

        // Limiter le nombre d'entrées pour les performances
        if (this.elements.logs.children.length > 50) {
            this.elements.logs.removeChild(this.elements.logs.lastChild!);
        }
    }

    private handleResize() {
        console.log("Adaptation de l'interface...");
    }
}

// Lancement automatique au chargement du DOM
window.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardManager();
    dashboard.addLog("Interface TypeScript chargée et prête.");

    // Simulation d'un flux de données constant pour le monitoring
    setInterval(() => {
        dashboard.updateStats({
            cpu: Math.floor(Math.random() * 15) + 5,
            fps: 28 + Math.floor(Math.random() * 4),
            gesture: Math.random() > 0.5 ? 'Palm_Open' : 'Index_Pinch',
            action: 'Tracking'
        });
    }, 1500);
});
