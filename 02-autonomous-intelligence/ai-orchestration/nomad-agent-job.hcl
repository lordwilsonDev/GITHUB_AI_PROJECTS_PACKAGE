# Nomad Job Specification for AI Agent
# Manages Python AI agents with automatic restarts and health checking

job "ai-agent-pool" {
  datacenters = ["dc1"]
  type = "service"

  group "agents" {
    count = 10  # Start with 10 agents, scale to 620+

    # Restart policy for fault tolerance
    restart {
      attempts = 3
      interval = "5m"
      delay    = "15s"
      mode     = "fail"
    }

    task "python-agent" {
      driver = "raw_exec"  # Native macOS process execution

      config {
        command = "/usr/bin/python3"
        args    = ["-u", "${NOMAD_TASK_DIR}/agent.py"]
      }

      # Resource allocation (soft limits)
      resources {
        cpu    = 200   # MHz
        memory = 512   # MB
      }

      # Environment variables
      env {
        AGENT_ID = "${NOMAD_ALLOC_ID}"
        NATS_URL = "nats://localhost:4222"
        CONSUL_ADDR = "http://localhost:8500"
      }

      # Health check
      service {
        name = "ai-agent"
        port = "http"
        
        check {
          type     = "http"
          path     = "/health"
          interval = "10s"
          timeout  = "2s"
        }
      }

      # Template for agent configuration
      template {
        data = <<EOH
{
  "agent_id": "{{ env "NOMAD_ALLOC_ID" }}",
  "nats_url": "{{ env "NATS_URL" }}",
  "temporal_host": "localhost:7233"
}
EOH
        destination = "local/config.json"
      }
    }
  }
}
