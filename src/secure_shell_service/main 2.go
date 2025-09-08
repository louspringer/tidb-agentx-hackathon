package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// CommandService implements the gRPC service
type CommandService struct {
	UnimplementedSecureShellServiceServer
}

// ExecuteCommand handles secure command execution
func (s *CommandService) ExecuteCommand(ctx context.Context, req *CommandRequest) (*CommandResponse, error) {
	// Validate command
	if req.Command == "" {
		return nil, status.Error(codes.InvalidArgument, "command cannot be empty")
	}

	// Set timeout
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()

	// Execute command with timeout
	cmd := exec.CommandContext(ctx, "bash", "-c", req.Command)
	output, err := cmd.CombinedOutput()

	if err != nil {
		return &CommandResponse{
			Success: false,
			Output:  string(output),
			Error:   err.Error(),
		}, nil
	}

	return &CommandResponse{
		Success: true,
		Output:  string(output),
		Error:   "",
	}, nil
}

// HealthCheck provides health status
func (s *CommandService) HealthCheck(ctx context.Context, req *HealthRequest) (*HealthResponse, error) {
	return &HealthResponse{
		Status: "healthy",
		Uptime: time.Now().Unix(),
	}, nil
}

func main() {
	port := os.Getenv("SHELL_SERVICE_PORT")
	if port == "" {
		port = "50051"
	}

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	RegisterSecureShellServiceServer(s, &CommandService{})

	log.Printf("🚀 Secure Shell Service listening on port %s", port)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
} 