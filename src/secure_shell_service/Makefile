# Secure Shell Service Makefile

.PHONY: build run test clean proto

# Build the Go service
build:
	@echo "🔨 Building secure shell service..."
	cd src/secure_shell_service && go build -o secure-shell-service main.go
	@echo "✅ Build complete"

# Generate protobuf code
proto:
	@echo "📝 Generating protobuf code..."
	cd src/secure_shell_service && protoc --go_out=. --go_opt=paths=source_relative \
		--go-grpc_out=. --go-grpc_opt=paths=source_relative secure_shell.proto
	@echo "✅ Protobuf generation complete"

# Run the service
run: build
	@echo "🚀 Starting secure shell service..."
	cd src/secure_shell_service && ./secure-shell-service

# Test the service
test:
	@echo "🧪 Testing secure shell service..."
	cd src/secure_shell_service && go test ./...

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	cd src/secure_shell_service && rm -f secure-shell-service
	@echo "✅ Clean complete"

# Install dependencies
deps:
	@echo "📦 Installing Go dependencies..."
	cd src/secure_shell_service && go mod tidy
	@echo "✅ Dependencies installed"

# Full setup
setup: deps proto build
	@echo "🎉 Secure shell service setup complete!"

# Help
help:
	@echo "Available targets:"
	@echo "  build   - Build the Go service"
	@echo "  proto   - Generate protobuf code"
	@echo "  run     - Build and run the service"
	@echo "  test    - Run tests"
	@echo "  clean   - Clean build artifacts"
	@echo "  deps    - Install dependencies"
	@echo "  setup   - Full setup (deps + proto + build)" 