package proxy

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"time"
)

const (
	caOrg          = "Flowspec Network Logger"
	caName         = "Flowspec CA"
	certValidDays  = 365 // Certificate validity period in days (1 year)
	// Note: Certificates must be renewed before expiry. To renew, delete
	// .logs/.certs/ directory and restart flowspec-netlog to regenerate.
	// Consider monitoring cert expiry with: openssl x509 -enddate -noout -in cert.pem
)

// CertManager handles CA certificate generation and storage
type CertManager struct {
	caCert     *x509.Certificate
	caKey      *rsa.PrivateKey
	tlsCA      tls.Certificate
	certDir    string
	certPath   string
	keyPath    string
	systemCert string
}

// NewCertManager creates or loads a CA certificate
func NewCertManager(logDir string) (*CertManager, error) {
	cm := &CertManager{
		certDir:    filepath.Join(logDir, ".certs"),
		certPath:   filepath.Join(logDir, ".certs", "flowspec-ca.crt"),
		keyPath:    filepath.Join(logDir, ".certs", "flowspec-ca.key"),
		systemCert: filepath.Join(logDir, ".certs", "flowspec-ca-system.crt"),
	}

	// Create cert directory
	if err := os.MkdirAll(cm.certDir, 0700); err != nil {
		return nil, fmt.Errorf("failed to create cert directory: %w", err)
	}

	// Check if cert already exists
	if _, err := os.Stat(cm.certPath); err == nil {
		return cm.loadExisting()
	}

	// Generate new CA
	return cm.generate()
}

// generate creates a new CA certificate and key
func (cm *CertManager) generate() (*CertManager, error) {
	// Generate RSA key
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return nil, fmt.Errorf("failed to generate key: %w", err)
	}
	cm.caKey = key

	// Create CA certificate
	serialNumber, err := rand.Int(rand.Reader, new(big.Int).Lsh(big.NewInt(1), 128))
	if err != nil {
		return nil, fmt.Errorf("failed to generate serial: %w", err)
	}

	notBefore := time.Now()
	notAfter := notBefore.Add(time.Duration(certValidDays) * 24 * time.Hour)

	template := x509.Certificate{
		SerialNumber: serialNumber,
		Subject: pkix.Name{
			Organization: []string{caOrg},
			CommonName:   caName,
		},
		NotBefore:             notBefore,
		NotAfter:              notAfter,
		KeyUsage:              x509.KeyUsageCertSign | x509.KeyUsageDigitalSignature,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
		IsCA:                  true,
	}

	derBytes, err := x509.CreateCertificate(rand.Reader, &template, &template, &key.PublicKey, key)
	if err != nil {
		return nil, fmt.Errorf("failed to create certificate: %w", err)
	}

	// Parse the certificate
	cert, err := x509.ParseCertificate(derBytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse certificate: %w", err)
	}
	cm.caCert = cert

	// Save to disk
	if err := cm.save(derBytes); err != nil {
		return nil, err
	}

	// Create TLS certificate
	cm.tlsCA = tls.Certificate{
		Certificate: [][]byte{derBytes},
		PrivateKey:  key,
		Leaf:        cert,
	}

	return cm, nil
}

// save writes the certificate and key to disk
func (cm *CertManager) save(derBytes []byte) (err error) {
	// Save certificate
	certOut, err := os.Create(cm.certPath)
	if err != nil {
		return fmt.Errorf("failed to create cert file: %w", err)
	}
	defer func() {
		// Check for errors when closing the cert file to prevent data loss
		if closeErr := certOut.Close(); closeErr != nil {
			err = fmt.Errorf("failed to close cert file (may have lost data): %w", closeErr)
		}
	}()

	if err := pem.Encode(certOut, &pem.Block{Type: "CERTIFICATE", Bytes: derBytes}); err != nil {
		return fmt.Errorf("failed to write cert: %w", err)
	}

	// Save key
	keyOut, err := os.OpenFile(cm.keyPath, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		return fmt.Errorf("failed to create key file: %w", err)
	}
	defer func() {
		// Check for errors when closing the key file to prevent data loss
		if closeErr := keyOut.Close(); closeErr != nil {
			err = fmt.Errorf("failed to close key file (may have lost data): %w", closeErr)
		}
	}()

	keyBytes := x509.MarshalPKCS1PrivateKey(cm.caKey)
	if err := pem.Encode(keyOut, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: keyBytes}); err != nil {
		return fmt.Errorf("failed to write key: %w", err)
	}

	// Create system-compatible cert (for installation)
	// Note: Certificate file is world-readable (0644) because it contains only the public
	// certificate, not the private key. The private key file above uses 0600 (owner-only)
	// to protect the secret key material. This follows standard CA certificate practices.
	if err := os.WriteFile(cm.systemCert, pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: derBytes}), 0644); err != nil {
		return fmt.Errorf("failed to write system cert: %w", err)
	}

	return nil
}

// loadExisting loads an existing CA certificate and key
func (cm *CertManager) loadExisting() (*CertManager, error) {
	// Load certificate
	certPEM, err := os.ReadFile(cm.certPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read cert: %w", err)
	}

	block, _ := pem.Decode(certPEM)
	if block == nil {
		return nil, fmt.Errorf("failed to decode cert PEM")
	}

	cert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse cert: %w", err)
	}
	cm.caCert = cert

	// Load key
	keyPEM, err := os.ReadFile(cm.keyPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read key: %w", err)
	}

	keyBlock, _ := pem.Decode(keyPEM)
	if keyBlock == nil {
		return nil, fmt.Errorf("failed to decode key PEM")
	}

	key, err := x509.ParsePKCS1PrivateKey(keyBlock.Bytes)
	if err != nil {
		return nil, fmt.Errorf("failed to parse key: %w", err)
	}
	cm.caKey = key

	// Create TLS certificate
	cm.tlsCA = tls.Certificate{
		Certificate: [][]byte{cert.Raw},
		PrivateKey:  key,
		Leaf:        cert,
	}

	return cm, nil
}

// GetTLSCA returns the TLS certificate for use with goproxy
func (cm *CertManager) GetTLSCA() *tls.Certificate {
	return &cm.tlsCA
}

// GetSystemCertPath returns the path to the system-compatible certificate
func (cm *CertManager) GetSystemCertPath() string {
	return cm.systemCert
}

// PrintInstallInstructions prints instructions for installing the CA certificate
func (cm *CertManager) PrintInstallInstructions() {
	fmt.Println("\nTo enable HTTPS interception, install the CA certificate:")
	fmt.Printf("\n  System-wide (requires sudo):\n")
	fmt.Printf("    sudo cp %s /usr/local/share/ca-certificates/flowspec-netlog.crt\n", cm.systemCert)
	fmt.Printf("    sudo update-ca-certificates\n")
	fmt.Printf("\n  Environment variable (current session):\n")
	fmt.Printf("    export NODE_EXTRA_CA_CERTS=%s\n", cm.systemCert)
	fmt.Printf("    export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt\n")
	fmt.Printf("\n  Or use without HTTPS interception (HTTP only)\n\n")
}
