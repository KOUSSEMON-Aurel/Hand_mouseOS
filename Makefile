.PHONY: all rust go cli clean help

# Variables
RUST_DIR := rust_core
CLI_DIR := cli
CLI_BIN := $(CLI_DIR)/handmouse
RUST_TARGET := $(RUST_DIR)/target/release/librust_mouse_filter.so

# Couleurs pour l'output
BLUE := \033[0;34m
GREEN := \033[0;32m
RESET := \033[0m

all: rust go

## Build Rust core library
rust:
	@echo "$(BLUE)🦀 Building Rust core...$(RESET)"
	@cd $(RUST_DIR) && cargo build --release
	@echo "$(GREEN)✅ Rust build complete$(RESET)"

## Build Go CLI
go: cli

cli:
	@echo "$(BLUE)🔨 Building Go CLI...$(RESET)"
	@cd $(CLI_DIR) && go build -o handmouse
	@echo "$(GREEN)✅ CLI build complete: $(CLI_BIN)$(RESET)"

## Clean build artifacts
clean:
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	@cd $(RUST_DIR) && cargo clean
	@rm -f $(CLI_BIN)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(RESET)"

## Show help
help:
	@echo "$(BLUE)Hand Mouse OS - Makefile$(RESET)"
	@echo ""
	@echo "Available targets:"
	@echo "  $(GREEN)make all$(RESET)     - Build Rust core and Go CLI"
	@echo "  $(GREEN)make rust$(RESET)    - Build Rust core library"
	@echo "  $(GREEN)make go$(RESET)      - Build Go CLI"
	@echo "  $(GREEN)make clean$(RESET)   - Clean all build artifacts"
	@echo "  $(GREEN)make help$(RESET)    - Show this help"
