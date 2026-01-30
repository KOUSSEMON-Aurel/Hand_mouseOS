package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var cfgFile string

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "handmouse",
	Short: "Hand Mouse OS - Contrôle de souris par gestes de la main",
	Long: `Hand Mouse OS est un système de contrôle de souris par vision par ordinateur.
Utilisez vos gestes de la main pour contrôler votre curseur et effectuer des actions.`,
}

// Execute adds all child commands to the root command and sets flags appropriately.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)

	// Persistent flags (disponibles pour toutes les sous-commandes)
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "fichier de configuration (défaut: $HOME/.handmouse.yaml)")
	rootCmd.PersistentFlags().BoolP("verbose", "v", false, "mode verbeux")
}

// initConfig lit le fichier de configuration et les variables d'environnement
func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		home, err := os.UserHomeDir()
		cobra.CheckErr(err)

		viper.AddConfigPath(home)
		viper.SetConfigType("yaml")
		viper.SetConfigName(".handmouse")
	}

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err == nil {
		if viper.GetBool("verbose") {
			fmt.Fprintln(os.Stderr, "Using config file:", viper.ConfigFileUsed())
		}
	}
}
