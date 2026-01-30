package tui

import (
	"fmt"
	"time"

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
		// Simuler des données (à remplacer par de vraies données IPC)
		m.fps = 60 + (int(time.Now().Unix()) % 10)

		gestures := []string{"Poing fermé", "Main ouverte", "Index pointé", "Pincement"}
		m.gestureName = gestures[int(time.Now().Unix()/2)%len(gestures)]

		m.cameraStatus = "✅ Actif"
		m.engineStatus = "✅ En cours"

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
