package ipc

import (
	"encoding/json"
	"fmt"
	"net"
)

const SocketPath = "/tmp/handmouse.sock"

// Command représente une commande IPC
type Command struct {
	Command string      `json:"command"`
	Value   interface{} `json:"value,omitempty"`
}

// Response représente une réponse IPC
type Response struct {
	Status  string                 `json:"status"`
	Message string                 `json:"message,omitempty"`
	Data    map[string]interface{} `json:"data,omitempty"`
}

// SendCommand envoie une commande à l'engine via IPC
func SendCommand(cmd Command) (*Response, error) {
	// Connexion au socket
	conn, err := net.Dial("unix", SocketPath)
	if err != nil {
		return nil, fmt.Errorf("impossible de se connecter à l'engine: %w", err)
	}
	defer conn.Close()

	// Encoder et envoyer la commande
	encoder := json.NewEncoder(conn)
	if err := encoder.Encode(cmd); err != nil {
		return nil, fmt.Errorf("erreur d'envoi de la commande: %w", err)
	}

	// Recevoir la réponse
	var response Response
	decoder := json.NewDecoder(conn)
	if err := decoder.Decode(&response); err != nil {
		return nil, fmt.Errorf("erreur de lecture de la réponse: %w", err)
	}

	return &response, nil
}

// GetStatus récupère le statut de l'engine
func GetStatus() (*Response, error) {
	return SendCommand(Command{Command: "get_status"})
}

// ToggleASL active/désactive l'ASL
func ToggleASL() (*Response, error) {
	return SendCommand(Command{Command: "toggle_asl"})
}

// SetASL définit l'état de l'ASL
func SetASL(enabled bool) (*Response, error) {
	return SendCommand(Command{Command: "set_asl", Value: enabled})
}
