package cmd

import (
	"fmt"
	"os/exec"

	"github.com/spf13/cobra"
)

var stopCmd = &cobra.Command{
	Use:   "stop",
	Short: "Arrête Hand Mouse OS",
	Long:  `Arrête proprement tous les processus de Hand Mouse OS.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("⏹️  Arrêt de Hand Mouse OS...")

		// Chercher et tuer les processus Python liés à Hand Mouse OS
		killCmd := exec.Command("pkill", "-f", "Hand_mouseOS")
		if err := killCmd.Run(); err != nil {
			fmt.Println("⚠️  Aucun processus Hand Mouse OS en cours d'exécution")
		} else {
			fmt.Println("✅ Hand Mouse OS arrêté")
		}
	},
}

func init() {
	rootCmd.AddCommand(stopCmd)
}
