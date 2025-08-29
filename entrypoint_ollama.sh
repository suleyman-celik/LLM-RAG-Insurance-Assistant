#!/bin/bash
set -e

# Start Ollama in the background.
/bin/ollama serve &
pid=$!

# Wait until Ollama API is available
# until curl -s http://localhost:11434/ >/dev/null 2>&1; do
#     echo "⏳ Waiting for Ollama server..."
#     sleep 2
# done

sleep 2

echo "🔴 Pulling Ollama phi3 model..."
ollama pull phi3
echo "🟢 Model ready!"

# Wait for Ollama process to finish
wait $pid
