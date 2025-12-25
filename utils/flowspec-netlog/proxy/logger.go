package proxy

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

const (
	maxBodySize = 1024 * 1024 // 1MB max body capture
)

// RequestLog represents a captured HTTP request/response
type RequestLog struct {
	Timestamp    string            `json:"timestamp"`
	Method       string            `json:"method"`
	URL          string            `json:"url"`
	Host         string            `json:"host"`
	StatusCode   int               `json:"status_code,omitempty"`
	Headers      map[string]string `json:"headers,omitempty"`
	RequestBody  string            `json:"request_body,omitempty"`
	ResponseBody string            `json:"response_body,omitempty"`
	Duration     int64             `json:"duration_ms,omitempty"`
	Error        string            `json:"error,omitempty"`
	Bypassed     bool              `json:"bypassed,omitempty"`
}

// Logger handles structured logging of HTTP traffic
type Logger struct {
	file     *os.File
	encoder  *json.Encoder
	logPath  string
	noProxy  map[string]bool
	maxBody  int
}

// NewLogger creates a new network logger
func NewLogger(logDir string) (*Logger, error) {
	timestamp := time.Now().Format("20060102-150405")
	logPath := filepath.Join(logDir, fmt.Sprintf("network.%s.jsonl", timestamp))

	file, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return nil, fmt.Errorf("failed to create log file: %w", err)
	}

	l := &Logger{
		file:     file,
		encoder:  json.NewEncoder(file),
		logPath:  logPath,
		noProxy:  parseNoProxy(),
		maxBody:  maxBodySize,
	}

	return l, nil
}

// parseNoProxy parses the NO_PROXY environment variable
func parseNoProxy() map[string]bool {
	noProxy := make(map[string]bool)
	envNoProxy := os.Getenv("NO_PROXY")
	if envNoProxy == "" {
		envNoProxy = os.Getenv("no_proxy")
	}

	if envNoProxy != "" {
		for _, host := range strings.Split(envNoProxy, ",") {
			host = strings.TrimSpace(host)
			if host != "" {
				noProxy[host] = true
			}
		}
	}

	return noProxy
}

// ShouldBypass checks if a host should bypass the proxy
func (l *Logger) ShouldBypass(host string) bool {
	// Check exact match
	if l.noProxy[host] {
		return true
	}

	// Check if host ends with any NO_PROXY entry (for wildcard domains)
	for noProxyHost := range l.noProxy {
		if strings.HasSuffix(host, "."+noProxyHost) || strings.HasSuffix(host, noProxyHost) {
			return true
		}
	}

	return false
}

// LogRequest logs an HTTP request
func (l *Logger) LogRequest(req *http.Request, startTime time.Time) *RequestLog {
	log := &RequestLog{
		Timestamp: startTime.Format(time.RFC3339),
		Method:    req.Method,
		URL:       req.URL.String(),
		Host:      req.Host,
		Headers:   make(map[string]string),
	}

	// Capture headers (selective to avoid clutter)
	importantHeaders := []string{
		"Content-Type",
		"Content-Length",
		"User-Agent",
		"Authorization",
		"X-Request-ID",
	}

	for _, h := range importantHeaders {
		if v := req.Header.Get(h); v != "" {
			log.Headers[h] = v
		}
	}

	// Capture request body if present and small enough
	if req.Body != nil && req.ContentLength > 0 && req.ContentLength < int64(l.maxBody) {
		body, err := io.ReadAll(io.LimitReader(req.Body, int64(l.maxBody)))
		if err == nil {
			log.RequestBody = string(body)
			// Restore body for forwarding
			req.Body = io.NopCloser(bytes.NewBuffer(body))
		}
	}

	return log
}

// LogResponse logs an HTTP response
func (l *Logger) LogResponse(log *RequestLog, resp *http.Response, startTime time.Time) error {
	log.StatusCode = resp.StatusCode
	log.Duration = time.Since(startTime).Milliseconds()

	// Capture response body if present and small enough
	if resp.Body != nil && resp.ContentLength > 0 && resp.ContentLength < int64(l.maxBody) {
		body, err := io.ReadAll(io.LimitReader(resp.Body, int64(l.maxBody)))
		if err == nil {
			// Only log text-based responses
			contentType := resp.Header.Get("Content-Type")
			if strings.Contains(contentType, "json") ||
				strings.Contains(contentType, "text") ||
				strings.Contains(contentType, "xml") {
				log.ResponseBody = string(body)
			}
			// Restore body
			resp.Body = io.NopCloser(bytes.NewBuffer(body))
		}
	}

	return l.Write(log)
}

// LogError logs a request with an error
func (l *Logger) LogError(log *RequestLog, err error) error {
	log.Error = err.Error()
	return l.Write(log)
}

// LogBypassed logs a bypassed request
func (l *Logger) LogBypassed(req *http.Request) error {
	log := &RequestLog{
		Timestamp: time.Now().Format(time.RFC3339),
		Method:    req.Method,
		URL:       req.URL.String(),
		Host:      req.Host,
		Bypassed:  true,
	}
	return l.Write(log)
}

// Write writes a log entry to the file
func (l *Logger) Write(log *RequestLog) error {
	return l.encoder.Encode(log)
}

// Close closes the log file
func (l *Logger) Close() error {
	if l.file != nil {
		return l.file.Close()
	}
	return nil
}

// GetLogPath returns the path to the log file
func (l *Logger) GetLogPath() string {
	return l.logPath
}

// Summary prints a summary of the log file
func (l *Logger) Summary() error {
	// Reopen file for reading
	file, err := os.Open(l.logPath)
	if err != nil {
		return err
	}
	defer file.Close()

	var total, errors, bypassed int
	methods := make(map[string]int)
	hosts := make(map[string]int)

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		var log RequestLog
		if err := json.Unmarshal(scanner.Bytes(), &log); err != nil {
			continue
		}

		total++
		if log.Error != "" {
			errors++
		}
		if log.Bypassed {
			bypassed++
		}
		methods[log.Method]++
		hosts[log.Host]++
	}

	fmt.Println("\n=== Network Capture Summary ===")
	fmt.Printf("Total requests: %d\n", total)
	fmt.Printf("Errors: %d\n", errors)
	fmt.Printf("Bypassed: %d\n", bypassed)
	fmt.Println("\nRequests by method:")
	for method, count := range methods {
		fmt.Printf("  %s: %d\n", method, count)
	}
	fmt.Println("\nTop hosts:")
	for host, count := range hosts {
		fmt.Printf("  %s: %d\n", host, count)
	}
	fmt.Printf("\nLog file: %s\n", l.logPath)

	return scanner.Err()
}
