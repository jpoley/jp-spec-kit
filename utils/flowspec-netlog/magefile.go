//go:build mage

package main

import (
	"fmt"
	"os"
	"runtime"

	"github.com/magefile/mage/mg"
	"github.com/magefile/mage/sh"
)

const (
	binary = "flowspec-netlog"
)

// Build compiles the flowspec-netlog binary
func Build() error {
	fmt.Println("Building flowspec-netlog...")
	return sh.Run("go", "build", "-o", binary, ".")
}

// Install installs the binary to /usr/local/bin (requires sudo)
func Install() error {
	mg.Deps(Build)
	fmt.Println("Installing flowspec-netlog to /usr/local/bin...")
	return sh.Run("sudo", "cp", binary, "/usr/local/bin/")
}

// Clean removes built artifacts
func Clean() error {
	fmt.Println("Cleaning...")
	os.Remove(binary)
	return nil
}

// Test runs the test suite
func Test() error {
	fmt.Println("Running tests...")
	return sh.Run("go", "test", "-v", "./...")
}

// Fmt formats Go code
func Fmt() error {
	fmt.Println("Formatting code...")
	return sh.Run("go", "fmt", "./...")
}

// Mod downloads and tidies dependencies
func Mod() error {
	fmt.Println("Downloading dependencies...")
	if err := sh.Run("go", "mod", "download"); err != nil {
		return err
	}
	fmt.Println("Tidying go.mod...")
	return sh.Run("go", "mod", "tidy")
}

// Dev builds and runs the proxy for development
func Dev() error {
	mg.Deps(Build)
	fmt.Println("Starting flowspec-netlog in dev mode...")
	fmt.Println("Set FLOWSPEC_CAPTURE_NETWORK=true to enable")
	return sh.Run("./"+binary, os.Args[1:]...)
}

// Dist builds binaries for multiple platforms
func Dist() error {
	platforms := []struct {
		os   string
		arch string
	}{
		{"linux", "amd64"},
		{"linux", "arm64"},
		{"darwin", "amd64"},
		{"darwin", "arm64"},
	}

	for _, p := range platforms {
		output := fmt.Sprintf("dist/%s-%s-%s", binary, p.os, p.arch)
		fmt.Printf("Building %s...\n", output)

		env := map[string]string{
			"GOOS":   p.os,
			"GOARCH": p.arch,
		}

		if err := sh.RunWith(env, "go", "build", "-o", output, "."); err != nil {
			return err
		}
	}

	return nil
}

// Info prints build information
func Info() {
	fmt.Printf("Go version: %s\n", runtime.Version())
	fmt.Printf("OS/Arch: %s/%s\n", runtime.GOOS, runtime.GOARCH)
	fmt.Printf("Binary: %s\n", binary)
}
