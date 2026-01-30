package cmd

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"runtime"

	"github.com/spf13/cobra"
)

var setupWebcamCmd = &cobra.Command{
	Use:   "webcam",
	Short: "Installe DroidCam pour utiliser votre téléphone comme webcam",
	Long:  `Détecte votre OS et installe automatiquement DroidCam pour une meilleure qualité vidéo.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("🔍 Détection de l'OS: %s...\n", runtime.GOOS)

		switch runtime.GOOS {
		case "linux":
			installDroidCamLinux()
		case "windows":
			installDroidCamWindows()
		default:
			fmt.Printf("❌ Désolé, l'installation automatique n'est pas supportée sur %s\n", runtime.GOOS)
		}
	},
}

func init() {
	setupCmd.AddCommand(setupWebcamCmd)
}

func installDroidCamLinux() {
	fmt.Println("🚀 Préparation de l'installation sur Linux...")

	distro := getLinuxDistro()
	fmt.Printf("📦 Distribution détectée: %s\n", distro)

	var installScript string

	switch distro {
	case "arch", "manjaro":
		fmt.Println("ℹ️ Tentative d'installation via AUR (besoin de yay ou pamac)...")
		installScript = "yay -S --noconfirm droidcam v4l2loopback-dkms || pamac install --no-confirm droidcam v4l2loopback-dkms"
	case "fedora":
		installScript = "sudo dnf install -y droidcam"
	default:
		// Fallback sur le script officiel pour Ubuntu/Debian/Autres
		fmt.Println("📦 Utilisation du script d'installation officiel (Source)...")
		installScript = `
			sudo apt-get update && sudo apt-get install -y linux-headers-$(uname -r) gcc make adb wget unzip
			cd /tmp
			wget -O droidcam_latest.zip https://www.dev47apps.com/files/linux/droidcam_1.8.2.zip
			unzip droidcam_latest.zip -d droidcam_setup
			cd droidcam_setup && sudo ./install-client
			sudo ./install-video
		`
	}

	runShellCommand(installScript)
}

func getLinuxDistro() string {
	out, err := exec.Command("sh", "-c", "grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '\"'").Output()
	if err != nil {
		return "unknown"
	}
	return string(out[:len(out)-1]) // remove newline
}

func installDroidCamWindows() {
	fmt.Println("🚀 Préparation de l'installation sur Windows...")
	installerUrl := "https://www.dev47apps.com/files/windows/droidcam_setup_6.5.2.exe"
	tempFile := os.TempDir() + "\\droidcam_setup.exe"

	fmt.Printf("📥 Téléchargement de l'installeur depuis %s...\n", installerUrl)
	err := downloadFile(tempFile, installerUrl)
	if err != nil {
		fmt.Printf("❌ Erreur de téléchargement: %v\n", err)
		return
	}

	fmt.Println("✅ Téléchargement terminé. Lancement de l'installeur...")
	exec.Command("explorer", tempFile).Start()
	fmt.Println("💡 Veuillez suivre les instructions à l'écran pour terminer l'installation.")
}

func runShellCommand(script string) {
	cmd := exec.Command("bash", "-c", script)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err := cmd.Run()
	if err != nil {
		fmt.Printf("❌ Erreur lors de l'exécution: %v\n", err)
	} else {
		fmt.Println("✅ Installation terminée avec succès !")
	}
}

func downloadFile(filepath string, url string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	return err
}
