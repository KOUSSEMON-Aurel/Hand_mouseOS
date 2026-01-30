package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/spf13/cobra"
)

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Lance l'engine en mode headless",
	Long:  `Démarre l'engine Hand Mouse OS sans interface graphique. La vidéo peut être affichée dans une fenêtre OpenCV séparée.`,
	Run: func(cmd *cobra.Command, args []string) {
		headless, _ := cmd.Flags().GetBool("headless")

		projectRoot, err := findProjectRoot()
		if err != nil {
			fmt.Fprintf(os.Stderr, "❌ Erreur: %v\n", err)
			os.Exit(1)
		}

		fmt.Println("🚀 Lancement de Hand Mouse OS (Mode Headless)...")

		// Construire la commande
		pythonPath := filepath.Join(projectRoot, "venv", "bin", "python")
		runnerPath := filepath.Join(projectRoot, "src", "headless_runner.py")

		cmdArgs := []string{runnerPath}
		if headless {
			cmdArgs = append(cmdArgs, "--no-video")
			fmt.Println("📹 Mode sans vidéo")
		} else {
			fmt.Println("📹 Fenêtre vidéo OpenCV activée")
		}

		// Lancer l'engine
		engineCmd := exec.Command(pythonPath, cmdArgs...)
		engineCmd.Stdout = os.Stdout
		engineCmd.Stderr = os.Stderr
		engineCmd.Dir = projectRoot

		if err := engineCmd.Run(); err != nil {
			fmt.Fprintf(os.Stderr, "❌ Erreur lors du lancement: %v\n", err)
			os.Exit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(runCmd)
	runCmd.Flags().BoolP("headless", "H", false, "Lance sans affichage vidéo")
}
