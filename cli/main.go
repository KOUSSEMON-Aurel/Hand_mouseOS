package main

import (
	"fmt"
	"os"

	"github.com/KOUSSEMON-Aurel/Hand_mouseOS/cli/cmd"
)

func main() {
	// Recovery for early crashes
	defer func() {
		if r := recover(); r != nil {
			fmt.Fprintf(os.Stderr, "CRITICAL PANIC: %v\n", r)
		}
	}()

	fmt.Fprintln(os.Stdout, "DEBUG: Hand Mouse OS CLI Starting...")
	cmd.Execute()
}
