# Gorilla Camping
A Flask site for off-grid nomads

## Running with Docker

This project includes a Docker setup for easy local development and deployment.

- **Python version:** 3.11 (as specified in the Dockerfile)
- **Exposed port:** 5000 (Flask default)
- **No required environment variables** are set by default, but you can add a `.env` file if needed (see `docker-compose.yml`).

### Build and Run

To build and start the app using Docker Compose:

```sh
docker compose up --build
```

The Flask app will be available at [http://localhost:5000](http://localhost:5000).

- The container runs as a non-root user for security.
- No external services (like databases) are required or configured by default.
- If you need to set environment variables, create a `.env` file in the project root and uncomment the `env_file` line in `docker-compose.yml`.
