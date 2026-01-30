package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/spf13/cobra"
)

var startCmd = &cobra.Command{
	Use:   "start",
	Short: "Démarre Hand Mouse OS",
	Long:  `Lance l'engine de tracking et l'interface graphique.`,
	Run: func(cmd *cobra.Command, args []string) {
		gui, _ := cmd.Flags().GetBool("gui")

		// Trouver le répertoire racine du projet
		projectRoot, err := findProjectRoot()
		if err != nil {
			fmt.Fprintf(os.Stderr, "❌ Erreur: %v\n", err)
			os.Exit(1)
		}

		if gui {
			fmt.Println("🚀 Lancement de Hand Mouse OS (GUI)...")
			runScript := filepath.Join(projectRoot, "master_run.sh")

			cmd := exec.Command("bash", runScript)
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			cmd.Dir = projectRoot

			if err := cmd.Run(); err != nil {
				fmt.Fprintf(os.Stderr, "❌ Erreur lors du lancement: %v\n", err)
				os.Exit(1)
			}
		} else {
			fmt.Println("🚀 Lancement de Hand Mouse OS (Mode headless)...")
			fmt.Println("⚠️  Mode headless non encore implémenté. Utilisez --gui pour le moment.")
		}
	},
}

func init() {
	rootCmd.AddCommand(startCmd)
	startCmd.Flags().BoolP("gui", "g", true, "Lance l'interface graphique Flet")
}

// findProjectRoot trouve le répertoire racine du projet (où se trouve main.py)
func findProjectRoot() (string, error) {
	// Essayer le répertoire courant
	if _, err := os.Stat("main.py"); err == nil {
		return os.Getwd()
	}

	// Essayer le parent du dossier cli
	wd, _ := os.Getwd()
	parent := filepath.Dir(wd)
	if _, err := os.Stat(filepath.Join(parent, "main.py")); err == nil {
		return parent, nil
	}

	return "", fmt.Errorf("impossible de trouver le répertoire racine du projet")
}
