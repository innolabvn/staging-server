# Multi-Service Docker Compose Project

This project contains two main services, managed together using a single `docker-compose.yml` file:

- **device-info-api**: A FastAPI-based Python service for collecting device information and analyzing source code.
- **ssh-server**: An Ubuntu-based SSH server with Docker pre-installed, useful for remote access and DevOps workflows.

## Folder Structure

- `collect_device/`: Source code and Dockerfile for the device info API (FastAPI, Python).
- `DockerBuildGenerator/`: Dockerfile and configuration for the Ubuntu SSH server.
- `docker-compose.yml`: Unified configuration to run both services together.

## How to Build and Run

1. **Clone this repository** (if you haven't already):
   ```sh
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. **Build and start all services:**
   ```sh
   docker-compose up --build
   ```
   This will build images and start both containers.

3. **Stop all services:**
   ```sh
   docker-compose down
   ```

## Service Details

### 1. device-info-api
- **Description:**
  - FastAPI app providing endpoints to get device info and analyze source code.
- **Exposed Port:** `8000`
- **API Endpoints:**
  - `GET /device-info` — Returns device hardware and OS information.
  - `GET /source-info?path=<local_path>` — Analyze local source code.
  - `GET /source-info?git_url=<repo_url>` — Analyze code from a git repository.

### 2. ssh-server
- **Description:**
  - Ubuntu container with SSH server and Docker installed. Useful for remote SSH access and running Docker commands inside the container.
- **Exposed Ports:**
  - `2222` (host) → `22` (container, SSH)
  - `8080` (host) → `80` (container, HTTP)
- **Default Credentials:**
  - User: `admin` / Password: `admin123`
  - Root: `root` / Password: `admin123`

## Customization
- You can modify the `docker-compose.yml` to change ports, volumes, or environment variables as needed.

## License
Specify your license here. 