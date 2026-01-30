package ipc

import (
	"encoding/json"
	"net"
	"os"
	"testing"
	"time"
)

func TestSendCommand(t *testing.T) {
	// Créer un socket temporaire pour le test
	originalSocket := SocketPath
	testSocket := "/tmp/handmouse_test.sock"
	SocketPath = testSocket
	defer func() { SocketPath = originalSocket }()

	// Nettoyer si le socket existe déjà
	os.Remove(testSocket)
	defer os.Remove(testSocket)

	// Lancer un serveur mock dans une goroutine
	ln, err := net.Listen("unix", testSocket)
	if err != nil {
		t.Fatalf("Failed to listen on test socket: %v", err)
	}
	defer ln.Close()

	go func() {
		conn, err := ln.Accept()
		if err != nil {
			return
		}
		defer conn.Close()

		var cmd Command
		decoder := json.NewDecoder(conn)
		if err := decoder.Decode(&cmd); err != nil {
			return
		}

		// Réponse mockée
		resp := Response{
			Status: "ok",
			Data:   map[string]interface{}{"is_processing": true},
		}
		encoder := json.NewEncoder(conn)
		encoder.Encode(resp)
	}()

	// Envoyer la commande via le client
	resp, err := GetStatus()
	if err != nil {
		t.Fatalf("SendCommand failed: %v", err)
	}

	if resp.Status != "ok" {
		t.Errorf("Expected status ok, got %s", resp.Status)
	}

	if val, ok := resp.Data["is_processing"].(bool); !ok || !val {
		t.Errorf("Expected is_processing true, got %v", resp.Data["is_processing"])
	}
}

func TestSendCommandRetry(t *testing.T) {
	// Teste que le client réessaie si le serveur n'est pas encore prêt
	originalSocket := SocketPath
	testSocket := "/tmp/handmouse_retry_test.sock"
	SocketPath = testSocket
	defer func() { SocketPath = originalSocket }()

	os.Remove(testSocket)
	defer os.Remove(testSocket)

	// On lance l'envoi APRÈS un court délai pour forcer le retry
	errChan := make(chan error)
	go func() {
		_, err := GetStatus()
		errChan <- err
	}()

	// Attendre un peu avant de lancer le serveur
	time.Sleep(1 * time.Second)

	ln, err := net.Listen("unix", testSocket)
	if err != nil {
		t.Fatalf("Failed to listen: %v", err)
	}
	defer ln.Close()

	go func() {
		conn, err := ln.Accept()
		if err != nil {
			return
		}
		defer conn.Close()
		json.NewEncoder(conn).Encode(Response{Status: "ok"})
	}()

	// Récupérer le résultat de SendCommand
	if err := <-errChan; err != nil {
		t.Errorf("SendCommand failed after retry: %v", err)
	}
}
