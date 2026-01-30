package tui

import (
	"fmt"
	"time"

	"github.com/KOUSSEMON-Aurel/Hand_mouseOS/cli/ipc"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Model représente l'état du dashboard
type Model struct {
	fps          int
	gestureName  string
	cameraStatus string
	engineStatus string
	width        int
	height       int
	quitting     bool
}

// tickMsg est envoyé à intervalles réguliers pour mettre à jour l'affichage
type tickMsg time.Time

func tickCmd() tea.Cmd {
	return tea.Tick(time.Millisecond*100, func(t time.Time) tea.Msg {
		return tickMsg(t)
	})
}

// InitialModel crée le modèle initial
func InitialModel() Model {
	return Model{
		fps:          0,
		gestureName:  "Aucun",
		cameraStatus: "Initialisation...",
		engineStatus: "Démarrage...",
	}
}

func (m Model) Init() tea.Cmd {
	return tickCmd()
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.quitting = true
			return m, tea.Quit
		}

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height

	case tickMsg:
		// Récupérer les vraies données via IPC
		resp, err := ipc.GetStatus()
		if err == nil && resp.Status == "ok" {
			// Données réelles de l'engine
			if fps, ok := resp.Data["fps"].(float64); ok {
				m.fps = int(fps)
			}
			if aslEnabled, ok := resp.Data["asl_enabled"].(bool); ok {
				if aslEnabled {
					m.gestureName = "Mode ASL actif"
				} else {
					m.gestureName = "Mode gestes standard"
				}
			}
			if isProcessing, ok := resp.Data["is_processing"].(bool); ok {
				if isProcessing {
					m.engineStatus = "✅ En cours"
				} else {
					m.engineStatus = "⏸️  En pause"
				}
			}
			m.cameraStatus = "✅ Actif"
		} else {
			// Engine non disponible
			m.cameraStatus = "❌ Déconnecté"
			m.engineStatus = "❌ Arrêté"
			m.gestureName = "N/A"
			m.fps = 0
		}

		return m, tickCmd()
	}

	return m, nil
}

func (m Model) View() string {
	if m.quitting {
		return "Au revoir! 👋\n"
	}

	// Styles
	titleStyle := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#00FF00")).
		MarginBottom(1)

	boxStyle := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("#874BFD")).
		Padding(1, 2).
		Width(40)

	labelStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#7D56F4")).
		Bold(true)

	valueStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#FAFAFA"))

	// Construction de l'interface
	title := titleStyle.Render("🤚 Hand Mouse OS - Dashboard")

	stats := fmt.Sprintf(
		"%s %s\n%s %s\n%s %s\n%s %d FPS",
		labelStyle.Render("Caméra:"),
		valueStyle.Render(m.cameraStatus),
		labelStyle.Render("Engine:"),
		valueStyle.Render(m.engineStatus),
		labelStyle.Render("Geste:"),
		valueStyle.Render(m.gestureName),
		labelStyle.Render("Performance:"),
		m.fps,
	)

	statsBox := boxStyle.Render(stats)

	help := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#626262")).
		Render("\nAppuyez sur 'q' pour quitter")

	return fmt.Sprintf("%s\n\n%s%s\n", title, statsBox, help)
}

// Run lance le dashboard TUI
func Run() error {
	p := tea.NewProgram(InitialModel(), tea.WithAltScreen())
	_, err := p.Run()
	return err
}
