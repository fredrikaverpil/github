package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	help := flag.Bool("help", false, "Show help")
	flag.Parse()

	if *help {
		flag.Usage()
		os.Exit(1)
	}

	fmt.Println("reposync hello")
}
