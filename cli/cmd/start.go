package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
)

var startCmd = &cobra.Command{
	Use:   "start",
	Short: "Démarre Hand Mouse OS",
	Long:  `Lance l'engine de tracking et l'interface graphique.`,
	Run: func(cmd *cobra.Command, args []string) {
		gui, _ := cmd.Flags().GetBool("gui")

		// 0. Vérification et configuration automatique des permissions (Linux uniquement)
		checkAndSetupUinput()

		// Trouver le binaire de l'engine (portable) ou le script (dev)
		exePath, err := os.Executable()
		if err != nil {
			fmt.Printf("DEBUG: Erreur os.Executable: %v\n", err)
			os.Exit(1)
		}
		exePath, _ = filepath.Abs(exePath)
		exeDir := filepath.Dir(exePath)
		println("DEBUG: Dossier exécutable:", exeDir)

		// 1. Chercher le binaire portable dans le même dossier ou handmouse-engine/handmouse-engine
		// En mode --onedir, l'exécutable est à l'intérieur du dossier handmouse-engine/
		enginePath := filepath.Join(exeDir, "handmouse-engine", "handmouse-engine")
		println("DEBUG: Test engine path 1:", enginePath)

		if _, err := os.Stat(enginePath); os.IsNotExist(err) {
			// Essayer chemin relatif direct (si mis à la racine linux/)
			enginePath = filepath.Join(exeDir, "handmouse-engine")
			println("DEBUG: Test engine path 2:", enginePath)
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

// checkAndSetupUinput vérifie si uinput est accessible et propose/exécute le setup si nécessaire
func checkAndSetupUinput() {
	if os.Getenv("GOOS") == "windows" {
		return
	}

	// Vérifier si /dev/uinput existe et est accessible en écriture
	f, err := os.OpenFile("/dev/uinput", os.O_WRONLY, 0660)
	if err == nil {
		f.Close()
		return // Tout est OK
	}

	fmt.Println("⚠️  Permissions /dev/uinput manquantes ou module non chargé.")
	fmt.Println("🛠️  Tentative de configuration automatique...")

	// Lancer la logique de setup permissions directement
	// On simule l'appel à setupPermissionsCmd.Run
	udevRule := `KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"`
	rulePath := "/etc/udev/rules.d/99-uinput.rules"

	// Demander sudo pour les opérations critiques
	fmt.Println("  - Chargement du module uinput et configuration udev (SUDO requis)...")

	setupCmds := []string{
		"sudo modprobe uinput",
		fmt.Sprintf("echo '%s' | sudo tee %s", udevRule, rulePath),
		"sudo udevadm control --reload-rules",
		"sudo udevadm trigger",
		"sudo chmod 666 /dev/uinput",
	}

	for _, c := range setupCmds {
		if err := exec.Command("bash", "-c", c).Run(); err != nil {
			fmt.Printf("❌ Échec de la commande [%s]: %v\n", c, err)
		}
	}

	// Vérifier si l'utilisateur est dans le groupe input
	user := os.Getenv("USER")
	groups, _ := exec.Command("groups", user).Output()
	if !contains(string(groups), "input") {
		fmt.Printf("  - Ajout de l'utilisateur %s au groupe 'input'...\n", user)
		exec.Command("sudo", "usermod", "-aG", "input", user).Run()
		fmt.Println("⚠️  NOTE : Vous devrez peut-être redémarrer votre session pour que les changements de groupe soient définitifs.")
	}

	fmt.Println("✅ Configuration automatique terminée.")
}

func contains(s, substr string) bool {
	return strings.Contains(s, substr)
}
