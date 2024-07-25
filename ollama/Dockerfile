# Dockerfile
FROM ollama/ollama:latest

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose the required port
EXPOSE 11434

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
