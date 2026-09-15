import json

def get_office_simulation_html(msg1: str = "", msg2: str = "", msg3: str = "") -> str:
    """
    Returns a self-contained HTML5 Canvas 2D office simulation.
    Features top-down law firm map with moving agents, waypoint navigation,
    and dynamic speech bubbles.
    """
    safe_msg1 = json.dumps(msg1[:250] if msg1 else "Reviewing document clauses at bookshelf...")
    safe_msg2 = json.dumps(msg2[:250] if msg2 else "Defending original terms at desk...")
    safe_msg3 = json.dumps(msg3[:250] if msg3 else "Delivering protective counter-offer...")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body {{ background: #0f172a; color: #f8fafc; padding: 12px; display: flex; flex-direction: column; align-items: center; }}
        #sim-container {{ position: relative; border-radius: 12px; overflow: hidden; border: 2px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        canvas {{ display: block; background: #1e293b; }}
        .hud {{
          position: absolute; top: 10px; left: 10px; right: 10px;
          display: flex; justify-content: space-between; pointer-events: none;
        }}
        .badge {{
          background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(4px);
          padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
          border: 1px solid #475569; display: flex; align-items: center; gap: 6px;
        }}
        .badge-alex {{ color: #38bdf8; border-color: #0284c7; }}
        .badge-morgan {{ color: #f43f5e; border-color: #e11d48; }}
        .log-box {{
          width: 100%; max-width: 760px; margin-top: 10px;
          background: #1e293b; border-radius: 8px; border: 1px solid #334155;
          padding: 10px 14px; font-size: 13px; min-height: 48px;
        }}
        .log-speaker {{ font-weight: bold; margin-right: 6px; }}
      </style>
    </head>
    <body>
      <div id="sim-container">
        <div class="hud">
          <div class="badge badge-alex"><span>🧑‍⚖️</span> Alex (Your Counsel)</div>
          <div class="badge" id="sim-status" style="color: #fbbf24;">📍 In Negotiation</div>
          <div class="badge badge-morgan"><span>🕴️</span> Morgan (Opposing Counsel)</div>
        </div>
        <canvas id="officeCanvas" width="760" height="380"></canvas>
      </div>
      <div class="log-box" id="live-dialogue">
        <span class="log-speaker" style="color: #38bdf8;">🧑‍⚖️ Alex:</span>
        <span id="log-text">Negotiation simulation initialized. Watch the agents move to the conference table...</span>
      </div>

      <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const statusEl = document.getElementById('sim-status');
        const logTextEl = document.getElementById('log-text');
        const dialogueBox = document.getElementById('live-dialogue');

        const dialogs = [
          {{ speaker: "Alex (Your Counsel)", color: "#38bdf8", text: {safe_msg1} }},
          {{ speaker: "Morgan (Opposing)", color: "#f43f5e", text: {safe_msg2} }},
          {{ speaker: "Alex (Your Counsel)", color: "#38bdf8", text: {safe_msg3} }}
        ];

        // Office Elements Definition
        const rooms = [
          {{ name: "RESEARCH LIBRARY", x: 30, y: 30, w: 200, h: 320, color: "#1e293b", floor: "#26354a" }},
          {{ name: "CONFERENCE ROOM", x: 260, y: 30, w: 240, h: 320, color: "#1e293b", floor: "#1e293b" }},
          {{ name: "OPPOSING OFFICE", x: 530, y: 30, w: 200, h: 320, color: "#1e293b", floor: "#273244" }}
        ];

        // Agents
        const agentAlex = {{
          x: 100, y: 120, targetX: 330, targetY: 190, speed: 1.4,
          color: "#0284c7", headColor: "#fde047", name: "Alex", avatar: "🧑‍⚖️",
          bubble: "", bubbleTimer: 0, bob: 0
        }};

        const agentMorgan = {{
          x: 650, y: 280, targetX: 430, targetY: 190, speed: 1.3,
          color: "#e11d48", headColor: "#fbbf24", name: "Morgan", avatar: "🕴️",
          bubble: "", bubbleTimer: 0, bob: 0
        }};

        let phase = 0; // 0: walking to table, 1: speech 1, 2: speech 2, 3: speech 3
        let speechStep = 0;
        let timer = 0;

        function drawOffice() {{
          // Draw floor
          ctx.fillStyle = "#0f172a";
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          // Draw Rooms
          rooms.forEach(r => {{
            ctx.fillStyle = r.floor;
            ctx.fillRect(r.x, r.y, r.w, r.h);
            ctx.strokeStyle = "#475569";
            ctx.lineWidth = 3;
            ctx.strokeRect(r.x, r.y, r.w, r.h);

            // Room labels
            ctx.fillStyle = "#64748b";
            ctx.font = "10px sans-serif";
            ctx.fillText(r.name, r.x + 10, r.y + 20);
          }});

          // Doorways / openings
          ctx.fillStyle = "#1e293b";
          ctx.fillRect(230, 160, 30, 60);
          ctx.fillRect(500, 160, 30, 60);

          // Furniture: Bookshelves in Library
          ctx.fillStyle = "#78350f";
          ctx.fillRect(45, 50, 20, 200);
          ctx.fillRect(45, 270, 80, 20);
          ctx.fillStyle = "#fbbf24";
          ctx.font = "9px sans-serif";
          ctx.fillText("📚 Case Law", 72, 80);

          // Conference Table & Chairs
          ctx.fillStyle = "#b45309"; // rich wood table
          ctx.beginPath();
          ctx.roundRect(330, 150, 100, 80, [16]);
          ctx.fill();
          ctx.strokeStyle = "#d97706";
          ctx.lineWidth = 2;
          ctx.stroke();

          // Table Doc Icon
          ctx.fillStyle = "#ffffff";
          ctx.font = "14px sans-serif";
          ctx.fillText("📄 ⚖️", 366, 196);

          // Chairs
          ctx.fillStyle = "#334155";
          ctx.fillRect(305, 175, 16, 30); // Left chair
          ctx.fillRect(439, 175, 16, 30); // Right chair

          // Furniture: Desk in Opposing office
          ctx.fillStyle = "#475569";
          ctx.fillRect(580, 80, 90, 40);
          ctx.fillStyle = "#94a3b8";
          ctx.font = "9px sans-serif";
          ctx.fillText("💻 Opposing Desk", 585, 105);

          // Plant in corner
          ctx.font = "18px sans-serif";
          ctx.fillText("🪴", 270, 70);
          ctx.fillText("🪴", 475, 70);
        }}

        function drawAgent(a) {{
          // Shadow
          ctx.fillStyle = "rgba(0,0,0,0.35)";
          ctx.beginPath();
          ctx.ellipse(a.x, a.y + 12, 10, 5, 0, 0, Math.PI * 2);
          ctx.fill();

          // Body
          const bobOffset = Math.sin(a.bob) * 2;
          ctx.fillStyle = a.color;
          ctx.beginPath();
          ctx.arc(a.x, a.y + bobOffset, 9, 0, Math.PI * 2);
          ctx.fill();

          // Head / Avatar
          ctx.font = "16px sans-serif";
          ctx.textAlign = "center";
          ctx.fillText(a.avatar, a.x, a.y - 7 + bobOffset);

          // Speech Bubble
          if (a.bubble) {{
            ctx.font = "11px sans-serif";
            const textWidth = Math.min(220, ctx.measureText(a.bubble).width + 20);
            const bx = Math.max(10, Math.min(canvas.width - textWidth - 10, a.x - textWidth / 2));
            const by = a.y - 45 + bobOffset;

            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.roundRect(bx, by, textWidth, 24, [6]);
            ctx.fill();
            ctx.strokeStyle = "#0f172a";
            ctx.lineWidth = 1;
            ctx.stroke();

            // Tail
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.moveTo(a.x - 4, by + 24);
            ctx.lineTo(a.x, by + 30);
            ctx.lineTo(a.x + 4, by + 24);
            ctx.fill();

            // Text
            ctx.fillStyle = "#0f172a";
            ctx.textAlign = "left";
            const displayText = a.bubble.length > 28 ? a.bubble.substring(0, 26) + "..." : a.bubble;
            ctx.fillText(displayText, bx + 8, by + 16);
          }}
        }}

        function updateAgent(a) {{
          const dx = a.targetX - a.x;
          const dy = a.targetY - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist > 2) {{
            a.x += (dx / dist) * a.speed;
            a.y += (dy / dist) * a.speed;
            a.bob += 0.2;
            return false;
          }} else {{
            a.x = a.targetX;
            a.y = a.targetY;
            return true;
          }}
        }}

        function loop() {{
          drawOffice();

          const alexArrived = updateAgent(agentAlex);
          const morganArrived = updateAgent(agentMorgan);

          drawAgent(agentAlex);
          drawAgent(agentMorgan);

          // State Machine
          if (phase === 0) {{
            statusEl.innerText = "🚶 Approaching Conference Table...";
            if (alexArrived && morganArrived) {{
              phase = 1;
              timer = 0;
            }}
          }} else if (phase === 1) {{
            statusEl.innerText = "🗣️ Alex Presenting Objection";
            agentAlex.bubble = dialogs[0].text;
            agentMorgan.bubble = "";
            logTextEl.innerText = dialogs[0].text;
            dialogueBox.style.borderColor = "#0284c7";
            timer++;
            if (timer > 180) {{
              phase = 2;
              timer = 0;
            }}
          }} else if (phase === 2) {{
            statusEl.innerText = "🗣️ Morgan Offering Compromise";
            agentAlex.bubble = "";
            agentMorgan.bubble = dialogs[1].text;
            logTextEl.innerText = dialogs[1].text;
            dialogueBox.style.borderColor = "#e11d48";
            timer++;
            if (timer > 180) {{
              phase = 3;
              timer = 0;
            }}
          }} else if (phase === 3) {{
            statusEl.innerText = "🤝 Finalizing Protective Terms";
            agentAlex.bubble = dialogs[2].text;
            agentMorgan.bubble = "";
            logTextEl.innerText = dialogs[2].text;
            dialogueBox.style.borderColor = "#10b981";
            timer++;
            if (timer > 220) {{
              statusEl.innerText = "✅ Negotiation Complete";
              phase = 4;
            }}
          }}

          requestAnimationFrame(loop);
        }}

        loop();
      </script>
    </body>
    </html>
    """
    return html_code
