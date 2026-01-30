/**
 * Module de gestion des événements clavier
 */

class KeyboardManager {
    private shortcuts: Map<string, () => void> = new Map();

    constructor() {
        this.initializeShortcuts();
        this.attachListeners();
    }

    private initializeShortcuts() {
        this.shortcuts.set('Ctrl+Space', () => this.toggleTracking());
        this.shortcuts.set('Ctrl+R', () => this.recalibrateCamera());
        this.shortcuts.set('Ctrl+S', () => this.saveSettings());
        this.shortcuts.set('Escape', () => this.stopEngine());
    }

    private attachListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }

    private handleKeyDown(event: KeyboardEvent) {
        const combo = this.getKeyCombo(event);
        const handler = this.shortcuts.get(combo);
        if (handler) {
            event.preventDefault();
            handler();
        }
    }

    private getKeyCombo(event: KeyboardEvent): string {
        const parts: string[] = [];
        if (event.ctrlKey) parts.push('Ctrl');
        if (event.shiftKey) parts.push('Shift');
        if (event.altKey) parts.push('Alt');
        parts.push(event.key);
        return parts.join('+');
    }

    private toggleTracking() { console.log('Toggle tracking'); }
    private recalibrateCamera() { console.log('Recalibrate'); }
    private saveSettings() { console.log('Save settings'); }
    private stopEngine() { console.log('Stop engine'); }
}

export const keyboard = new KeyboardManager();
