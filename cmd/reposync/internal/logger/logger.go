package logger

import (
	"context"
	"io"
	"log/slog"
	"os"
	"strings"
)

// Logger is the application logger.
type Logger struct {
	*slog.Logger
}

// New creates a new application logger with timestamps removed.
func New() *Logger {
	opts := &slog.HandlerOptions{
		Level: slog.LevelInfo,
		ReplaceAttr: func(_ []string, a slog.Attr) slog.Attr {
			if a.Key == "time" {
				return slog.Attr{} // Skip time attribute
			}
			return a
		},
	}
	handler := slog.NewTextHandler(os.Stderr, opts)
	return &Logger{
		Logger: slog.New(handler),
	}
}

// NewPlainTextLogger creates a logger for usage and help text that doesn't use key/value format.
func NewPlainTextLogger() *Logger {
	handler := &plainTextHandler{w: os.Stderr}
	return &Logger{
		Logger: slog.New(handler),
	}
}

// Custom handler for plain text output without timestamps and key/value pairs.
type plainTextHandler struct {
	w io.Writer
}

func (h *plainTextHandler) Enabled(_ context.Context, _ slog.Level) bool {
	return true
}

func (h *plainTextHandler) Handle(_ context.Context, r slog.Record) error {
	var message strings.Builder
	message.WriteString(r.Message)
	message.WriteString("\n")

	_, err := io.WriteString(h.w, message.String())
	return err
}

func (h *plainTextHandler) WithAttrs(_ []slog.Attr) slog.Handler {
	return h
}

func (h *plainTextHandler) WithGroup(_ string) slog.Handler {
	return h
}
