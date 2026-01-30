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

		// Trouver le binaire de l'engine (portable) ou le script (dev)
		exePath, _ := os.Executable()
		exeDir := filepath.Dir(exePath)

		// 1. Chercher le binaire portable dans le même dossier ou handmouse-engine/handmouse-engine
		enginePath := filepath.Join(exeDir, "handmouse-engine", "handmouse-engine")
		if _, err := os.Stat(enginePath); os.IsNotExist(err) {
			// Essayer chemin relatif direct (si mis à la racine linux/)
			enginePath = filepath.Join(exeDir, "handmouse-engine")
		}

		if gui {
			if _, err := os.Stat(enginePath); err == nil {
				fmt.Printf("🚀 Lancement de Hand Mouse OS (Portable GUI: %s)...\n", enginePath)
				cmd := exec.Command(enginePath)
				cmd.Stdout = os.Stdout
				cmd.Stderr = os.Stderr
				cmd.Dir = filepath.Dir(enginePath)
				if err := cmd.Run(); err != nil {
					fmt.Fprintf(os.Stderr, "❌ Erreur lors du lancement portable: %v\n", err)
					os.Exit(1)
				}
				return
			}

			// Fallback mode développement
			fmt.Println("🚀 Lancement de Hand Mouse OS (Mode Développement)...")
			projectRoot, err := findProjectRoot()
			if err != nil {
				fmt.Fprintf(os.Stderr, "❌ Erreur: %v\n", err)
				os.Exit(1)
			}
			runScript := filepath.Join(projectRoot, "master_run.sh")
			cmd := exec.Command("bash", runScript)
			cmd.Stdout = os.Stdout
			cmd.Stderr = os.Stderr
			cmd.Dir = projectRoot
			if err := cmd.Run(); err != nil {
				fmt.Fprintf(os.Stderr, "❌ Erreur lors du lancement script: %v\n", err)
				os.Exit(1)
			}
		} else {
			fmt.Println("🚀 Lancement de Hand Mouse OS (Mode headless)...")
			fmt.Println("⚠️  Mode headless non encore implémenté via binaire portable.")
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
