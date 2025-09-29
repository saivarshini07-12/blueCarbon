#!/bin/bash

# YourCarbonFootprint Docker Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the application (build if needed)"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo "  build     Build the Docker image"
    echo "  logs      Show application logs"
    echo "  status    Show container status"
    echo "  clean     Stop and remove containers, networks, and images"
    echo "  help      Show this help message"
    echo ""
    echo "Environment:"
    echo "  Make sure you have created a .env file with your GROQ_API_KEY"
    echo ""
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file and add your GROQ_API_KEY before starting the application"
        return 1
    fi
    
    if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=your_groq_api_key_here" .env; then
        print_warning "GROQ_API_KEY not set in .env file"
        print_info "Please edit .env file and add your actual GROQ_API_KEY"
        return 1
    fi
    
    return 0
}

start_app() {
    print_info "Starting YourCarbonFootprint application..."
    
    if ! check_env; then
        return 1
    fi
    
    docker-compose up --build -d
    
    print_success "Application started successfully!"
    print_info "Access the application at: http://localhost:8501"
    print_info "Use '$0 logs' to view application logs"
    print_info "Use '$0 status' to check container status"
}

stop_app() {
    print_info "Stopping YourCarbonFootprint application..."
    docker-compose down
    print_success "Application stopped successfully!"
}

restart_app() {
    print_info "Restarting YourCarbonFootprint application..."
    stop_app
    start_app
}

build_app() {
    print_info "Building YourCarbonFootprint Docker image..."
    docker-compose build --no-cache
    print_success "Build completed successfully!"
}

show_logs() {
    print_info "Showing application logs (Press Ctrl+C to exit)..."
    docker-compose logs -f yourcarbonfootprint
}

show_status() {
    print_info "Container status:"
    docker-compose ps
    
    if docker-compose ps | grep -q "Up"; then
        print_success "Application is running"
        print_info "Access at: http://localhost:8501"
    else
        print_warning "Application is not running"
        print_info "Use '$0 start' to start the application"
    fi
}

clean_app() {
    print_warning "This will stop and remove all containers, networks, and images"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker-compose down -v --rmi all --remove-orphans
        print_success "Cleanup completed!"
    else
        print_info "Cleanup cancelled"
    fi
}

# Main script logic
case "${1:-help}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    build)
        build_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_app
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        print_error "Unknown command: $1"
        print_usage
        exit 1
        ;;
esac
