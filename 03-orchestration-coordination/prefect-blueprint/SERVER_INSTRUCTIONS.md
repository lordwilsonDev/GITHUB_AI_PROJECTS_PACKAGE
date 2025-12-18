# Prefect Server Setup Instructions

## Step 1.5: Start Prefect Server (Terminal B)

### What This Does
The Prefect Server is the **Control Plane** that:
- Serves the REST/GraphQL API at `http://127.0.0.1:4200/api`
- Provides the web UI at `http://127.0.0.1:4200`
- Manages the SQLite database (stored in `~/.prefect`)
- Runs the scheduler that evaluates deployment schedules

### How to Start the Server

**Option 1: Using the provided script**
```bash
cd ~/prefect-blueprint
bash start_server.sh
```

**Option 2: Manual commands**
```bash
cd ~/prefect-blueprint
source .venv/bin/activate
prefect server start
```

### Important Notes

1. **Keep Terminal B Open**: This process MUST remain running. Do not close this terminal window.

2. **Expected Output**: You should see:
   ```
   Starting Prefect server...
   ✓ Server started at http://127.0.0.1:4200
   ```

3. **Services Started**:
   - UI: React-based web interface
   - API: REST/GraphQL endpoints
   - Database: Asynchronous SQLite database
   - Scheduler: Loop that evaluates deployment schedules

4. **Verify Server is Running**:
   - Open browser to `http://127.0.0.1:4200`
   - You should see the Prefect UI

### Next Steps

Once the server is running:
1. Keep this terminal (Terminal B) open
2. Open a new terminal (Terminal A) for client commands
3. Configure the API URL in Terminal A (Step 1.6)

### Troubleshooting

- **Port already in use**: If port 4200 is already in use, stop any existing Prefect server
- **Permission errors**: Ensure the virtual environment is activated
- **Database errors**: Check `~/.prefect` directory permissions

---

**Status**: Ready to start
**Terminal**: B (Server Terminal)
**Action Required**: Run the start command and keep terminal open
