package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"

	"github.com/spf13/cobra"
)

var setupPermissionsCmd = &cobra.Command{
	Use:   "permissions",
	Short: "Configure les permissions pour le contrôle de la souris sans sudo",
	Long: `Ajoute les règles udev nécessaires et configure les groupes d'utilisateurs 
pour permettre à Hand Mouse OS de contrôler le curseur (via uinput) sans accès root.`,
	Run: func(cmd *cobra.Command, args []string) {
		if runtime.GOOS != "linux" {
			fmt.Println("❌ Cette commande est uniquement disponible sur Linux.")
			return
		}

		fmt.Println("🛠️ Configuration des permissions uinput...")

		// 1. Créer la règle udev
		udevRule := `KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"`
		rulePath := "/etc/udev/rules.d/99-uinput.rules"

		fmt.Printf("  - Création de %s...\n", rulePath)
		ruleCmd := fmt.Sprintf("echo '%s' | sudo tee %s", udevRule, rulePath)
		if err := exec.Command("bash", "-c", ruleCmd).Run(); err != nil {
			fmt.Printf("❌ Erreur lors de la création de la règle udev: %v\n", err)
			return
		}

		// 2. Ajouter l'utilisateur au groupe input
		user := os.Getenv("USER")
		if user == "" {
			userOutput, _ := exec.Command("whoami").Output()
			user = string(userOutput)
		}
		fmt.Printf("  - Ajout de l'utilisateur %s au groupe 'input'...\n", user)
		if err := exec.Command("sudo", "usermod", "-aG", "input", user).Run(); err != nil {
			fmt.Printf("❌ Erreur lors de l'ajout au groupe: %v\n", err)
			return
		}

		// 3. Appliquer chmod immédiat
		fmt.Println("  - Application des droits temporaires sur /dev/uinput...")
		if err := exec.Command("sudo", "chmod", "666", "/dev/uinput").Run(); err != nil {
			fmt.Printf("⚠️ Note: Impossible de modifier /dev/uinput (peut ne pas exister encore): %v\n", err)
		}

		fmt.Println("\n✅ Configuration terminée avec succès !")
		fmt.Println("⚠️  IMPORTANT : Vous devez redémarrer votre session (ou votre PC) pour que les changements de groupe soient actifs.")
		fmt.Println("🚀 Vous pouvez maintenant lancer : ./handmouse start")
	},
}

func init() {
	setupCmd.AddCommand(setupPermissionsCmd)
}
