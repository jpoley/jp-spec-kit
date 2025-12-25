package proxy

import (
	"fmt"
	"net/http"
	"time"

	"github.com/elazarl/goproxy"
)

// Proxy wraps goproxy with logging capabilities
type Proxy struct {
	*goproxy.ProxyHttpServer
	logger  *Logger
	certMgr *CertManager
}

// NewProxy creates a new logging proxy server
func NewProxy(logDir string) (*Proxy, error) {
	// Create logger
	logger, err := NewLogger(logDir)
	if err != nil {
		return nil, fmt.Errorf("failed to create logger: %w", err)
	}

	// Create certificate manager
	certMgr, err := NewCertManager(logDir)
	if err != nil {
		return nil, fmt.Errorf("failed to create cert manager: %w", err)
	}

	// Create goproxy instance
	proxy := goproxy.NewProxyHttpServer()
	proxy.Verbose = false // Disable goproxy's own logging

	// Set up HTTPS handling
	ca := certMgr.GetTLSCA()
	if ca != nil {
		goproxy.GoproxyCa = *ca
		proxy.OnRequest().HandleConnect(goproxy.AlwaysMitm)
	}

	p := &Proxy{
		ProxyHttpServer: proxy,
		logger:          logger,
		certMgr:         certMgr,
	}

	// Set up request/response handlers
	p.setupHandlers()

	// Print CA installation instructions
	certMgr.PrintInstallInstructions()

	return p, nil
}

// setupHandlers configures the proxy request/response handlers
func (p *Proxy) setupHandlers() {
	// Handle all requests
	p.OnRequest().DoFunc(func(req *http.Request, ctx *goproxy.ProxyCtx) (*http.Request, *http.Response) {
		// Check if request should be bypassed
		if p.logger.ShouldBypass(req.Host) {
			p.logger.LogBypassed(req)
			return req, nil
		}

		// Log request
		startTime := time.Now()
		ctx.UserData = &struct {
			log       *RequestLog
			startTime time.Time
		}{
			log:       p.logger.LogRequest(req, startTime),
			startTime: startTime,
		}

		return req, nil
	})

	// Handle all responses
	p.OnResponse().DoFunc(func(resp *http.Response, ctx *goproxy.ProxyCtx) *http.Response {
		// Skip if request was bypassed or no user data
		if ctx.UserData == nil {
			return resp
		}

		// Safe type assertion to prevent panic if UserData is unexpected type
		data, ok := ctx.UserData.(*struct {
			log       *RequestLog
			startTime time.Time
		})
		if !ok {
			// UserData is not the expected type, skip logging
			return resp
		}

		// Log response
		if resp != nil {
			p.logger.LogResponse(data.log, resp, data.startTime)
		} else if ctx.Error != nil {
			p.logger.LogError(data.log, ctx.Error)
		}

		return resp
	})
}

// Close closes the proxy and its resources
func (p *Proxy) Close() error {
	// Print summary
	if err := p.logger.Summary(); err != nil {
		fmt.Printf("Warning: failed to print summary: %v\n", err)
	}

	return p.logger.Close()
}

// GetLogPath returns the path to the log file
func (p *Proxy) GetLogPath() string {
	return p.logger.GetLogPath()
}

// GetCertPath returns the path to the CA certificate
func (p *Proxy) GetCertPath() string {
	return p.certMgr.GetSystemCertPath()
}
