package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/jpoley/flowspec/utils/flowspec-netlog/proxy"
)

const (
	defaultPort = "8080"
	version     = "0.1.0"
)

func main() {
	// Check if network capture is enabled
	if os.Getenv("FLOWSPEC_CAPTURE_NETWORK") != "true" {
		fmt.Println("flowspec-netlog: FLOWSPEC_CAPTURE_NETWORK not set to 'true', exiting")
		os.Exit(0)
	}

	// Get log directory
	logDir := os.Getenv("LOG_DIR")
	if logDir == "" {
		logDir = ".logs"
	}

	// Create log directory if it doesn't exist
	if err := os.MkdirAll(logDir, 0755); err != nil {
		log.Fatalf("Failed to create log directory: %v", err)
	}

	port := os.Getenv("FLOWSPEC_NETLOG_PORT")
	if port == "" {
		port = defaultPort
	}

	// Initialize proxy with logging
	p, err := proxy.NewProxy(logDir)
	if err != nil {
		log.Fatalf("Failed to create proxy: %v", err)
	}
	defer p.Close()

	// Set up graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	// Start proxy server
	addr := ":" + port
	server := &http.Server{
		Addr:    addr,
		Handler: p,
	}

	go func() {
		fmt.Printf("flowspec-netlog v%s starting on %s\n", version, addr)
		fmt.Printf("Logging to: %s/network.*.jsonl\n", logDir)
		fmt.Printf("Press Ctrl+C to stop\n")
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Proxy server error: %v", err)
		}
	}()

	// Wait for shutdown signal
	<-sigChan
	fmt.Println("\nShutting down flowspec-netlog...")

	// Create shutdown context with timeout
	shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer shutdownCancel()

	// Gracefully shutdown server
	if err := server.Shutdown(shutdownCtx); err != nil {
		log.Printf("Server shutdown error: %v", err)
	}
}
