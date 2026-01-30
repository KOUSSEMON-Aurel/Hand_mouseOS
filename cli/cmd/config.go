package cmd

import (
	"fmt"
	"os"

	"github.com/KOUSSEMON-Aurel/Hand_mouseOS/cli/ipc"
	"github.com/spf13/cobra"
)

var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Gère la configuration de Hand Mouse OS",
	Long:  `Permet de configurer l'engine en temps réel (ASL, sensibilité, etc.)`,
}

var configSetCmd = &cobra.Command{
	Use:   "set [key] [value]",
	Short: "Définit une valeur de configuration",
	Args:  cobra.ExactArgs(2),
	Run: func(cmd *cobra.Command, args []string) {
		key := args[0]
		value := args[1]

		switch key {
		case "asl":
			enabled := value == "true" || value == "1" || value == "on"
			resp, err := ipc.SetASL(enabled)
			if err != nil {
				fmt.Fprintf(os.Stderr, "❌ Erreur: %v\n", err)
				os.Exit(1)
			}
			if resp.Status == "ok" {
				fmt.Printf("✅ ASL: %v\n", enabled)
			} else {
				fmt.Fprintf(os.Stderr, "❌ %s\n", resp.Message)
			}
		default:
			fmt.Fprintf(os.Stderr, "❌ Clé inconnue: %s\n", key)
			os.Exit(1)
		}
	},
}

var configGetCmd = &cobra.Command{
	Use:   "get [key]",
	Short: "Récupère une valeur de configuration",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		key := args[0]

		resp, err := ipc.GetStatus()
		if err != nil {
			fmt.Fprintf(os.Stderr, "❌ Erreur: %v\n", err)
			os.Exit(1)
		}

		if resp.Status != "ok" {
			fmt.Fprintf(os.Stderr, "❌ %s\n", resp.Message)
			os.Exit(1)
		}

		switch key {
		case "asl":
			fmt.Printf("ASL: %v\n", resp.Data["asl_enabled"])
		case "status":
			fmt.Printf("Processing: %v\n", resp.Data["is_processing"])
		default:
			fmt.Fprintf(os.Stderr, "❌ Clé inconnue: %s\n", key)
			os.Exit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(configCmd)
	configCmd.AddCommand(configSetCmd)
	configCmd.AddCommand(configGetCmd)
}
