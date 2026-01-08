//go:build mage
// +build mage

// Backend Build Automation with Mage
// This is a reference magefile.go for React Frontend + Go Backend stack.
// Copy this to your backend/ directory and customize as needed.
//
// Install Mage: go install github.com/magefile/mage@latest
// List targets: mage -l
// Run target: mage build
// Run with verbose: mage -v build

package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"github.com/magefile/mage/mg"
	"github.com/magefile/mage/sh"
)

const (
	// Build configuration
	binaryName    = "api"
	mainPath      = "./cmd/api"
	outputDir     = "./bin"
	coverageFile  = "coverage.out"
	coverageHTML  = "coverage.html"

	// Security and SBOM
	auditJSON     = "go-audit.json"
	sbomJSON      = "sbom.json"
	sbomXML       = "sbom.xml"

	// Tool versions (update as needed)
	golangciLintVersion = "v1.55.2"
	gosecVersion        = "latest"
	cyclonedxVersion    = "v1.5.0"
)

// Default target when running `mage` without arguments
var Default = Build

// Build builds the Go binary with version embedding and optimizations
func Build() error {
	mg.Deps(InstallDeps)

	fmt.Println("🏗️  Building binary...")

	version, err := getVersion()
	if err != nil {
		return err
	}

	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}

	outputPath := filepath.Join(outputDir, binaryName)
	if runtime.GOOS == "windows" {
		outputPath += ".exe"
	}

	ldflags := fmt.Sprintf("-s -w -X main.Version=%s -X main.BuildTime=%s",
		version,
		time.Now().Format(time.RFC3339))

	args := []string{
		"build",
		"-ldflags", ldflags,
		"-o", outputPath,
		mainPath,
	}

	if err := sh.Run("go", args...); err != nil {
		return fmt.Errorf("build failed: %w", err)
	}

	fmt.Printf("✅ Built %s (version: %s)\n", outputPath, version)
	return nil
}

// BuildRelease builds an optimized production binary
func BuildRelease() error {
	mg.Deps(InstallDeps)

	fmt.Println("🏗️  Building production binary...")

	version, err := getVersion()
	if err != nil {
		return err
	}

	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return fmt.Errorf("failed to create output directory: %w", err)
	}

	outputPath := filepath.Join(outputDir, binaryName)
	if runtime.GOOS == "windows" {
		outputPath += ".exe"
	}

	ldflags := fmt.Sprintf("-s -w -X main.Version=%s -X main.BuildTime=%s",
		version,
		time.Now().Format(time.RFC3339))

	args := []string{
		"build",
		"-ldflags", ldflags,
		"-trimpath",
		"-o", outputPath,
		mainPath,
	}

	env := map[string]string{
		"CGO_ENABLED": "0",
	}

	if err := sh.RunWith(env, "go", args...); err != nil {
		return fmt.Errorf("build failed: %w", err)
	}

	// Calculate SHA256 digest
	digest, err := calculateDigest(outputPath)
	if err != nil {
		fmt.Printf("⚠️  Warning: Could not calculate digest: %v\n", err)
	} else {
		digestPath := outputPath + ".sha256"
		if err := os.WriteFile(digestPath, []byte(digest), 0644); err != nil {
			fmt.Printf("⚠️  Warning: Could not write digest file: %v\n", err)
		} else {
			fmt.Printf("📝 Digest: %s\n", digest)
		}
	}

	fmt.Printf("✅ Built production binary: %s (version: %s)\n", outputPath, version)
	return nil
}

// Test runs all tests with coverage
func Test() error {
	fmt.Println("🧪 Running tests...")

	args := []string{
		"test",
		"-v",
		"-race",
		"-coverprofile=" + coverageFile,
		"-covermode=atomic",
		"./...",
	}

	if err := sh.Run("go", args...); err != nil {
		return fmt.Errorf("tests failed: %w", err)
	}

	// Generate HTML coverage report
	if err := sh.Run("go", "tool", "cover", "-html="+coverageFile, "-o", coverageHTML); err != nil {
		fmt.Printf("⚠️  Warning: Could not generate HTML coverage report: %v\n", err)
	} else {
		fmt.Printf("📊 Coverage report: %s\n", coverageHTML)
	}

	// Show coverage summary
	if err := sh.Run("go", "tool", "cover", "-func="+coverageFile); err != nil {
		fmt.Printf("⚠️  Warning: Could not show coverage summary: %v\n", err)
	}

	fmt.Println("✅ Tests passed")
	return nil
}

// TestShort runs short tests (excludes integration tests)
func TestShort() error {
	fmt.Println("🧪 Running short tests...")

	args := []string{
		"test",
		"-v",
		"-short",
		"-race",
		"./...",
	}

	if err := sh.Run("go", args...); err != nil {
		return fmt.Errorf("tests failed: %w", err)
	}

	fmt.Println("✅ Short tests passed")
	return nil
}

// Lint runs golangci-lint
func Lint() error {
	fmt.Println("🔍 Running linter...")

	if err := ensureGolangciLint(); err != nil {
		return err
	}

	args := []string{
		"run",
		"--timeout", "5m",
		"./...",
	}

	if err := sh.Run("golangci-lint", args...); err != nil {
		return fmt.Errorf("linting failed: %w", err)
	}

	fmt.Println("✅ Linting passed")
	return nil
}

// Format formats Go code with gofmt
func Format() error {
	fmt.Println("✨ Formatting code...")

	if err := sh.Run("gofmt", "-s", "-w", "."); err != nil {
		return fmt.Errorf("formatting failed: %w", err)
	}

	fmt.Println("✅ Code formatted")
	return nil
}

// Tidy runs go mod tidy
func Tidy() error {
	fmt.Println("🧹 Tidying dependencies...")

	if err := sh.Run("go", "mod", "tidy"); err != nil {
		return fmt.Errorf("go mod tidy failed: %w", err)
	}

	fmt.Println("✅ Dependencies tidied")
	return nil
}

// Verify verifies go.mod and go.sum are up to date
func Verify() error {
	fmt.Println("🔍 Verifying go.mod and go.sum...")

	if err := sh.Run("go", "mod", "verify"); err != nil {
		return fmt.Errorf("verification failed: %w", err)
	}

	// Check if go.mod and go.sum need tidying
	if err := sh.Run("go", "mod", "tidy"); err != nil {
		return fmt.Errorf("go mod tidy failed: %w", err)
	}

	// Check for changes
	output, err := sh.Output("git", "status", "--porcelain", "go.mod", "go.sum")
	if err != nil {
		fmt.Printf("⚠️  Warning: Could not check git status: %v\n", err)
	} else if output != "" {
		return fmt.Errorf("go.mod or go.sum is not up to date, run 'go mod tidy'")
	}

	fmt.Println("✅ go.mod and go.sum are up to date")
	return nil
}

// Security runs security scans (gosec + govulncheck)
func Security() error {
	mg.Deps(SecuritySAST, SecuritySCA)
	fmt.Println("✅ All security scans completed")
	return nil
}

// SecuritySAST runs gosec (static application security testing)
func SecuritySAST() error {
	fmt.Println("🔒 Running SAST scan (gosec)...")

	if err := ensureGosec(); err != nil {
		return err
	}

	args := []string{
		"-fmt", "json",
		"-out", "gosec-report.json",
		"-no-fail",
		"./...",
	}

	// gosec returns non-zero exit code if issues found, but we want to continue
	_ = sh.Run("gosec", args...)

	// Check if report was generated
	if _, err := os.Stat("gosec-report.json"); err == nil {
		fmt.Println("📄 SAST report: gosec-report.json")
	}

	fmt.Println("✅ SAST scan completed")
	return nil
}

// SecuritySCA runs govulncheck (software composition analysis)
func SecuritySCA() error {
	fmt.Println("🔒 Running SCA scan (govulncheck)...")

	if err := ensureGovulncheck(); err != nil {
		return err
	}

	args := []string{
		"-json",
		"./...",
	}

	output, err := sh.Output("govulncheck", args...)
	if err != nil {
		// govulncheck returns non-zero if vulnerabilities found
		fmt.Printf("⚠️  Vulnerabilities found:\n%s\n", output)
	}

	// Write output to file
	if err := os.WriteFile("govulncheck-report.json", []byte(output), 0644); err != nil {
		fmt.Printf("⚠️  Warning: Could not write govulncheck report: %v\n", err)
	} else {
		fmt.Println("📄 SCA report: govulncheck-report.json")
	}

	fmt.Println("✅ SCA scan completed")
	return nil
}

// SBOM generates Software Bill of Materials (CycloneDX format)
func SBOM() error {
	fmt.Println("📋 Generating SBOM...")

	if err := ensureCycloneDX(); err != nil {
		return err
	}

	// Generate JSON SBOM
	jsonArgs := []string{
		"mod",
		"-json",
		"-output", sbomJSON,
	}

	if err := sh.Run("cyclonedx-gomod", jsonArgs...); err != nil {
		return fmt.Errorf("SBOM generation (JSON) failed: %w", err)
	}

	fmt.Printf("✅ Generated SBOM (JSON): %s\n", sbomJSON)

	// Generate XML SBOM
	xmlArgs := []string{
		"mod",
		"-output", sbomXML,
	}

	if err := sh.Run("cyclonedx-gomod", xmlArgs...); err != nil {
		return fmt.Errorf("SBOM generation (XML) failed: %w", err)
	}

	fmt.Printf("✅ Generated SBOM (XML): %s\n", sbomXML)

	return nil
}

// Clean removes build artifacts and generated files
func Clean() error {
	fmt.Println("🧹 Cleaning build artifacts...")

	filesToRemove := []string{
		outputDir,
		coverageFile,
		coverageHTML,
		auditJSON,
		sbomJSON,
		sbomXML,
		"gosec-report.json",
		"govulncheck-report.json",
	}

	for _, file := range filesToRemove {
		if err := sh.Rm(file); err != nil {
			fmt.Printf("⚠️  Warning: Could not remove %s: %v\n", file, err)
		}
	}

	fmt.Println("✅ Cleaned build artifacts")
	return nil
}

// InstallDeps ensures all Go dependencies are installed
func InstallDeps() error {
	fmt.Println("📦 Installing dependencies...")

	if err := sh.Run("go", "mod", "download"); err != nil {
		return fmt.Errorf("failed to download dependencies: %w", err)
	}

	return nil
}

// All runs all quality checks (format, lint, test, security, SBOM)
func All() error {
	mg.Deps(Format, Lint, Test, Security, SBOM, Build)
	fmt.Println("✅ All checks passed!")
	return nil
}

// CI runs all CI checks (lint, test, security, SBOM, build)
func CI() error {
	mg.Deps(Lint, Test, Security, SBOM, BuildRelease)
	fmt.Println("✅ CI checks passed!")
	return nil
}

// ================================================================================
// Helper Functions
// ================================================================================

func getVersion() (string, error) {
	// Try to get version from git describe
	version, err := sh.Output("git", "describe", "--tags", "--always", "--dirty")
	if err != nil {
		// Fallback to commit hash
		hash, err := sh.Output("git", "rev-parse", "--short", "HEAD")
		if err != nil {
			// Fallback to dev version
			return "dev", nil
		}
		return hash, nil
	}
	return strings.TrimSpace(version), nil
}

func calculateDigest(filePath string) (string, error) {
	cmd := exec.Command("sha256sum", filePath)
	if runtime.GOOS == "darwin" {
		cmd = exec.Command("shasum", "-a", "256", filePath)
	}

	output, err := cmd.Output()
	if err != nil {
		return "", err
	}

	// Extract just the hash (first field)
	fields := strings.Fields(string(output))
	if len(fields) == 0 {
		return "", fmt.Errorf("unexpected output format")
	}

	return fields[0], nil
}

func ensureGolangciLint() error {
	// Check if golangci-lint is installed
	if err := sh.Run("golangci-lint", "--version"); err == nil {
		return nil
	}

	fmt.Printf("📥 Installing golangci-lint %s...\n", golangciLintVersion)

	// Use go install for safe, static command execution (avoids shell injection)
	if err := sh.Run("go", "install", "github.com/golangci/golangci-lint/cmd/golangci-lint@"+golangciLintVersion); err != nil {
		return fmt.Errorf("failed to install golangci-lint: %w", err)
	}

	fmt.Println("✅ Installed golangci-lint")
	return nil
}

func ensureGosec() error {
	// Check if gosec is installed
	if err := sh.Run("gosec", "-version"); err == nil {
		return nil
	}

	fmt.Println("📥 Installing gosec...")

	if err := sh.Run("go", "install", "github.com/securego/gosec/v2/cmd/gosec@"+gosecVersion); err != nil {
		return fmt.Errorf("failed to install gosec: %w", err)
	}

	fmt.Println("✅ Installed gosec")
	return nil
}

func ensureGovulncheck() error {
	// Check if govulncheck is installed
	if err := sh.Run("govulncheck", "-version"); err == nil {
		return nil
	}

	fmt.Println("📥 Installing govulncheck...")

	if err := sh.Run("go", "install", "golang.org/x/vuln/cmd/govulncheck@latest"); err != nil {
		return fmt.Errorf("failed to install govulncheck: %w", err)
	}

	fmt.Println("✅ Installed govulncheck")
	return nil
}

func ensureCycloneDX() error {
	// Check if cyclonedx-gomod is installed
	if err := sh.Run("cyclonedx-gomod", "-version"); err == nil {
		return nil
	}

	fmt.Println("📥 Installing cyclonedx-gomod...")

	if err := sh.Run("go", "install", "github.com/CycloneDX/cyclonedx-gomod/cmd/cyclonedx-gomod@"+cyclonedxVersion); err != nil {
		return fmt.Errorf("failed to install cyclonedx-gomod: %w", err)
	}

	fmt.Println("✅ Installed cyclonedx-gomod")
	return nil
}
