#!/usr/bin/env python3
"""
LLM Conductor Server - Web interface for orchestration.

This module provides a FastAPI web server with WebSocket support for
real-time orchestration monitoring.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration import CollaborativeConductor, FastCollaborativeConductor
from agents import AGENT_PRESETS

app = FastAPI(
    title="LLM Conductor",
    description="Multi-Agent AI Orchestration System",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
DEFAULT_AGENT = os.environ.get("DEFAULT_AGENT", "claude")
connected_clients: List[WebSocket] = []


def get_html_interface(default_agent: str = "claude") -> str:
    """Generate the HTML interface with agent selection."""
    agent_options = "\n".join([
        f'<option value="{name}" {"selected" if name == default_agent else ""}>{config.name}</option>'
        for name, config in sorted(AGENT_PRESETS.items())
    ])

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>LLM Conductor - Multi-Agent AI Orchestration</title>
    <style>
        body {{
            font-family: 'Monaco', 'Menlo', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1 {{
            color: #569cd6;
            font-size: 24px;
            margin-bottom: 20px;
        }}

        .input-section {{
            background: #252526;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }}

        input[type="text"] {{
            flex: 1;
            min-width: 300px;
            padding: 10px;
            background: #3c3c3c;
            border: 1px solid #464647;
            color: #d4d4d4;
            font-family: inherit;
            font-size: 14px;
            border-radius: 4px;
        }}

        select {{
            padding: 10px;
            background: #3c3c3c;
            border: 1px solid #464647;
            color: #d4d4d4;
            font-family: inherit;
            font-size: 14px;
            border-radius: 4px;
        }}

        button {{
            padding: 10px 20px;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 4px;
            font-family: inherit;
            cursor: pointer;
        }}

        button:hover {{
            background: #005a9e;
        }}

        .toggle-section {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .toggle-switch {{
            position: relative;
            width: 60px;
            height: 28px;
        }}

        .toggle-switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}

        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 28px;
        }}

        .slider:before {{
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}

        input:checked + .slider {{
            background-color: #4ec9b0;
        }}

        input:checked + .slider:before {{
            transform: translateX(32px);
        }}

        .mode-label {{
            color: #4ec9b0;
            font-weight: bold;
        }}

        .output-section {{
            background: #1e1e1e;
            border: 1px solid #464647;
            border-radius: 8px;
            padding: 20px;
            height: 600px;
            overflow-y: auto;
        }}

        .output-line {{
            margin: 2px 0;
            font-size: 13px;
            line-height: 1.4;
        }}

        .timestamp {{
            color: #858585;
        }}

        .tool-output {{
            color: #c586c0;
        }}

        .phase-header {{
            color: #dcdcaa;
            font-weight: bold;
            margin: 10px 0;
            border-bottom: 1px solid #464647;
            padding-bottom: 5px;
        }}

        .status-connected {{
            color: #4ec9b0;
            font-size: 12px;
        }}

        .status-disconnected {{
            color: #f44747;
            font-size: 12px;
        }}

        .speed-indicator {{
            font-size: 18px;
        }}

        .agent-label {{
            color: #9cdcfe;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            <span id="speed-indicator" class="speed-indicator">⚡</span> LLM Conductor
            <span id="status" class="status-disconnected">● Disconnected</span>
        </h1>

        <div class="input-section">
            <input type="text" id="task-input" placeholder="Enter a task to orchestrate..."
                   value="Create a simple calculator web app">
            <select id="agent-select">
                {agent_options}
            </select>
            <button onclick="orchestrate()">Orchestrate</button>
            <button onclick="clearOutput()">Clear</button>

            <div class="toggle-section">
                <span>Mode:</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="speed-toggle" checked onchange="toggleSpeed()">
                    <span class="slider"></span>
                </label>
                <span id="mode-label" class="mode-label">FAST</span>
            </div>
        </div>

        <div class="output-section" id="output">
            <div class="output-line">⚡ Ready for orchestration...</div>
            <div class="output-line agent-label">Select an agent and enter a task to begin.</div>
        </div>
    </div>

    <script>
        let ws = null;
        const output = document.getElementById('output');
        const status = document.getElementById('status');
        const taskInput = document.getElementById('task-input');
        const agentSelect = document.getElementById('agent-select');
        const speedToggle = document.getElementById('speed-toggle');
        const modeLabel = document.getElementById('mode-label');
        const speedIndicator = document.getElementById('speed-indicator');

        function connect() {{
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${{protocol}}//${{window.location.host}}/ws`);

            ws.onopen = () => {{
                status.textContent = '● Connected';
                status.className = 'status-connected';
                addOutput('Connected to LLM Conductor server', 'system');
            }};

            ws.onmessage = (event) => {{
                const data = JSON.parse(event.data);

                if (data.type === 'output' || data.type === 'agent_output') {{
                    addOutput(data.line, data.tool || data.agent, data.timestamp);
                }} else if (data.type === 'phase') {{
                    addPhaseHeader(data.phase);
                }} else if (data.type === 'project_created') {{
                    addOutput(`Project created: ${{data.project_name}}`, 'system');
                    addOutput(`Using agent: ${{data.agent}}`, 'system');
                }} else if (data.type === 'orchestration_complete') {{
                    addPhaseHeader(`✅ Complete! Created ${{data.files_created}} files in ${{data.duration?.toFixed(1) || '?'}}s`);
                }}
            }};

            ws.onclose = () => {{
                status.textContent = '● Disconnected';
                status.className = 'status-disconnected';
                addOutput('Disconnected from server', 'system');
                setTimeout(connect, 3000);
            }};
        }}

        function addOutput(line, tool = 'system', timestamp = null) {{
            const div = document.createElement('div');
            div.className = 'output-line';

            if (timestamp) {{
                div.innerHTML = `<span class="timestamp">[${{timestamp}}]</span> `;
            }}

            if (tool !== 'system') {{
                div.innerHTML += `<span class="tool-output">${{tool}}:</span> `;
            }}

            div.innerHTML += escapeHtml(line);

            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }}

        function addPhaseHeader(phase) {{
            const div = document.createElement('div');
            div.className = 'phase-header';
            div.textContent = phase;
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }}

        function orchestrate() {{
            const task = taskInput.value.trim();
            if (!task) return;

            const isFast = speedToggle.checked;
            const agent = agentSelect.value;

            if (ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{
                    action: 'orchestrate',
                    task: task,
                    fast: isFast,
                    agent: agent
                }}));
                addPhaseHeader(`Starting ${{isFast ? 'FAST' : 'DETAILED'}} orchestration with ${{agent}}: ${{task}}`);
            }}
        }}

        function clearOutput() {{
            const isFast = speedToggle.checked;
            output.innerHTML = `<div class="output-line">${{isFast ? '⚡' : '🎭'}} Ready for ${{isFast ? 'fast' : 'detailed'}} orchestration...</div>`;
        }}

        function toggleSpeed() {{
            const isFast = speedToggle.checked;
            modeLabel.textContent = isFast ? 'FAST' : 'DETAILED';
            speedIndicator.textContent = isFast ? '⚡' : '🎭';
            speedIndicator.style.color = isFast ? '#ffcc00' : '#569cd6';
            clearOutput();
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        // Connect on load
        connect();

        // Enter key submits
        taskInput.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') orchestrate();
        }});
    </script>
</body>
</html>
    """


@app.get("/")
async def get_index():
    """Serve the HTML interface."""
    return HTMLResponse(get_html_interface(DEFAULT_AGENT))


@app.get("/api/agents")
async def list_agents():
    """List available agent presets."""
    return {
        "agents": [
            {"id": name, "name": config.name, "command": config.command}
            for name, config in sorted(AGENT_PRESETS.items())
        ],
        "default": DEFAULT_AGENT
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time orchestration output."""
    await websocket.accept()
    connected_clients.append(websocket)

    # Create conductor instances for this connection
    conductors = {}

    # Output handler for real-time updates
    async def output_handler(data):
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    try:
        while True:
            data = await websocket.receive_json()

            if data['action'] == 'orchestrate':
                agent = data.get('agent', DEFAULT_AGENT)
                is_fast = data.get('fast', True)
                task = data['task']

                # Create or reuse conductor
                conductor_key = f"{agent}_{is_fast}"
                if conductor_key not in conductors:
                    if is_fast:
                        conductors[conductor_key] = FastCollaborativeConductor(agent_preset=agent)
                    else:
                        conductors[conductor_key] = CollaborativeConductor(agent_preset=agent)
                    conductors[conductor_key].add_output_handler(output_handler)

                conductor = conductors[conductor_key]

                # Run orchestration in background
                asyncio.create_task(conductor.orchestrate(task))

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        # Clean up conductors
        for conductor in conductors.values():
            conductor.remove_output_handler(output_handler)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agents": list(AGENT_PRESETS.keys())}


def main():
    """Run the server."""
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8200"))

    print(f"⚡ Starting LLM Conductor server on http://{host}:{port}")
    print(f"   Default agent: {DEFAULT_AGENT}")
    print(f"   Available agents: {', '.join(AGENT_PRESETS.keys())}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
