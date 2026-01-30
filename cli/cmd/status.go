package cmd

import (
	"fmt"
	"os/exec"
	"strings"

	"github.com/spf13/cobra"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Affiche l'état de Hand Mouse OS",
	Long:  `Vérifie si Hand Mouse OS est en cours d'exécution et affiche les informations système.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("📊 État de Hand Mouse OS\n")

		// Vérifier si le processus est en cours
		checkCmd := exec.Command("pgrep", "-f", "Hand_mouseOS")
		output, err := checkCmd.Output()

		if err != nil || len(output) == 0 {
			fmt.Println("❌ Hand Mouse OS n'est pas en cours d'exécution")
		} else {
			pids := strings.TrimSpace(string(output))
			fmt.Printf("✅ Hand Mouse OS est actif (PID: %s)\n", pids)
		}

		// Vérifier les dépendances système
		fmt.Println("\n🔍 Vérification des dépendances:")
		checkDependency("Python", "python3", "--version")
		checkDependency("Caméra", "v4l2-ctl", "--list-devices")
		checkDependency("uinput", "test", "-w", "/dev/uinput")
	},
}

func checkDependency(name, command string, args ...string) {
	cmd := exec.Command(command, args...)
	if err := cmd.Run(); err != nil {
		fmt.Printf("  ⚠️  %s: Non disponible\n", name)
	} else {
		fmt.Printf("  ✅ %s: OK\n", name)
	}
}

func init() {
	rootCmd.AddCommand(statusCmd)
}
