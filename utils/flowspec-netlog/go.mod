module github.com/jpoley/flowspec/utils/flowspec-netlog

go 1.21

require (
	// goproxy: HTTP/HTTPS proxy library with MITM support for request/response interception
	// Using commit hash instead of tagged release because:
	// - Latest stable features needed for HTTPS MITM certificate handling
	// - No suitable tagged release available at time of integration
	// SECURITY: Commit hash pinning provides reproducible builds but requires manual updates
	// MAINTENANCE: Monitor https://github.com/elazarl/goproxy/releases for official releases
	// TODO: Migrate to tagged release when available (check periodically)
	github.com/elazarl/goproxy v0.0.0-20231117061959-7cc037d33fb5

	// mage: Build automation tool (alternative to Make)
	// Used for: Build tasks, cross-platform compilation, dependency management
	// Using tagged release v1.15.0 for stability and reproducibility
	github.com/magefile/mage v1.15.0
)
