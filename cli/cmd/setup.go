package cmd

import (
	"github.com/spf13/cobra"
)

// setupCmd represents the setup command
var setupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Configure les composants système de Hand Mouse OS",
	Long:  `Permet d'installer les dépendances externes comme les drivers de webcam ou les permissions.`,
}

func init() {
	rootCmd.AddCommand(setupCmd)
}
