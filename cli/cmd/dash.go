package cmd

import (
	"fmt"
	"os"

	"github.com/KOUSSEMON-Aurel/Hand_mouseOS/cli/tui"
	"github.com/spf13/cobra"
)

var dashCmd = &cobra.Command{
	Use:   "dash",
	Short: "Ouvre le tableau de bord interactif",
	Long:  `Lance une interface TUI (Terminal User Interface) pour monitorer Hand Mouse OS en temps réel.`,
	Run: func(cmd *cobra.Command, args []string) {
		if err := tui.Run(); err != nil {
			fmt.Fprintf(os.Stderr, "❌ Erreur: %v\n", err)
			os.Exit(1)
		}
	},
}

func init() {
	rootCmd.AddCommand(dashCmd)
}
