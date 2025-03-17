package main

import (
	"flag"
	"os"

	"github.com/fredrikaverpil/github/cmd/reposync/internal/logger"
)

func main() {
	// Set up logger
	log := logger.New()

	// Define the top-level flags
	var targetDir string
	flag.StringVar(&targetDir, "dir", ".", "Target directory to operate on")

	// Early parse to get target directory
	flag.Parse()

	// Check if the directory exists
	if _, err := os.Stat(targetDir); os.IsNotExist(err) {
		log.Error("Directory does not exist", "dir", targetDir)
		os.Exit(1)
	}

	// Get subcommand
	args := flag.Args()
	if len(args) < 1 {
		printUsage()
		os.Exit(1)
	}

	// Handle subcommands
	switch args[0] {
	case "detect":
		log.Info("Detecting project types", "dir", targetDir)
		// runDetect(targetDir, args[1:])
	case "dependabot":
		log.Info("Generating dependabot configuration", "dir", targetDir)
		// runDependabot(targetDir, args[1:])
	case "sync":
		log.Info("Syncing workflows", "dir", targetDir)
		// runSync(targetDir, args[1:])
	default:
		log.Error("Unknown command", "command", args[0])
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	// Use a plain text handler for usage output
	usageLog := logger.NewPlainTextLogger()

	usageLog.Info("Usage: reposync [global flags] <command> [command flags]")
	usageLog.Info("\nGlobal flags:")

	flag.VisitAll(func(f *flag.Flag) {
		usageLog.Info("  -" + f.Name + "  " + f.Usage + " (default: " + f.DefValue + ")")
	})

	usageLog.Info("\nCommands:")
	usageLog.Info("  detect      Detect project types in a repository")
	usageLog.Info("  dependabot  Generate dependabot configuration")
	usageLog.Info("  sync        Sync workflows based on detected types")
}
