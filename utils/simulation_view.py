import json

def get_office_simulation_html(msg1: str = "", msg2: str = "", msg3: str = "") -> str:
    """
    Returns an authentic 16-bit RPG pixel-art legal simulation map
    styled after Stanford's Generative Agents (Smallville).
    Features procedural pixel textures, animated sprites, and retro callout cards.
    """
    safe_msg1 = json.dumps(msg1[:280] if msg1 else "Reviewing clause liabilities in legal library...")
    safe_msg2 = json.dumps(msg2[:280] if msg2 else "Opposing counsel defending original contract terms...")
    safe_msg3 = json.dumps(msg3[:280] if msg3 else "Delivering protective counter-offer terms...")

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: "Courier New", monospace, sans-serif; }}
        body {{
          background: #111827;
          color: #f3f4f6;
          padding: 8px;
          display: flex;
          flex-direction: column;
          align-items: center;
        }}
        #sim-wrapper {{
          position: relative;
          border-radius: 8px;
          border: 4px solid #374151;
          box-shadow: 0 12px 30px rgba(0,0,0,0.7);
          overflow: hidden;
          background: #1f2937;
        }}
        canvas {{
          display: block;
          image-rendering: pixelated;
          image-rendering: crisp-edges;
        }}
        .overlay-callout {{
          position: absolute;
          background: rgba(17, 24, 39, 0.92);
          border: 2px solid #60a5fa;
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 11px;
          max-width: 260px;
          box-shadow: 0 4px 14px rgba(0,0,0,0.5);
          pointer-events: none;
        }}
        .callout-title {{
          font-weight: bold;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 4px;
        }}
        .hud-banner {{
          position: absolute;
          top: 8px; left: 8px; right: 8px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          pointer-events: none;
        }}
        .retro-tag {{
          background: #1e293b;
          border: 2px solid #475569;
          padding: 4px 10px;
          font-size: 11px;
          font-weight: bold;
          border-radius: 4px;
        }}
        .retro-dialogue-box {{
          width: 100%;
          max-width: 800px;
          margin-top: 10px;
          background: #0f172a;
          border: 3px solid #475569;
          border-radius: 6px;
          padding: 12px 16px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.6);
          display: flex;
          flex-direction: column;
          gap: 6px;
        }}
        .retro-line {{
          font-size: 12px;
          line-height: 1.4;
        }}
        .speaker-tag {{
          font-weight: bold;
          padding: 1px 4px;
          border-radius: 2px;
        }}
      </style>
    </head>
    <body>
      <div id="sim-wrapper">
        <div class="hud-banner">
          <div class="retro-tag" style="color: #38bdf8; border-color: #0284c7;">🧑‍⚖️ AGENT ALEX (LEGAL COUNSEL)</div>
          <div class="retro-tag" id="activity-label" style="color: #facc15; border-color: #ca8a04;">📍 PREPARING IN LAW LIBRARY</div>
          <div class="retro-tag" style="color: #f87171; border-color: #dc2626;">🕴️ AGENT MORGAN (OPPOSING)</div>
        </div>
        <canvas id="rpgCanvas" width="800" height="420"></canvas>
      </div>

      <div class="retro-dialogue-box">
        <div style="font-size: 10px; color: #94a3b8; font-weight: bold; text-transform: uppercase;">
          📜 Live Agent Dialogue & Negotiation Feed
        </div>
        <div class="retro-line" id="dialogue-feed">
          <span class="speaker-tag" style="background: #0369a1; color: #fff;">ALEX:</span>
          <span id="feed-text" style="color: #e2e8f0;">Agents are moving to their positions on the office map...</span>
        </div>
      </div>

      <script>
        const canvas = document.getElementById('rpgCanvas');
        const ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = false;

        const activityLabel = document.getElementById('activity-label');
        const feedText = document.getElementById('feed-text');
        const dialogueFeed = document.getElementById('dialogue-feed');

        const dialogues = [
          {{ speaker: "ALEX", tagBg: "#0369a1", text: {safe_msg1} }},
          {{ speaker: "MORGAN", tagBg: "#b91c1c", text: {safe_msg2} }},
          {{ speaker: "ALEX", tagBg: "#0369a1", text: {safe_msg3} }}
        ];

        // --- 16-BIT RETRO TILE DRAWING HELPERS ---
        function drawWoodFloor(x, y, w, h) {{
          ctx.fillStyle = "#a16207"; // warm wood
          ctx.fillRect(x, y, w, h);
          // Plank lines
          ctx.strokeStyle = "#854d0e";
          ctx.lineWidth = 1;
          for (let py = y; py < y + h; py += 12) {{
            ctx.beginPath();
            ctx.moveTo(x, py);
            ctx.lineTo(x + w, py);
            ctx.stroke();
          }}
          for (let px = x; px < x + w; px += 36) {{
            for (let py = y; py < y + h; py += 24) {{
              ctx.beginPath();
              ctx.moveTo(px, py);
              ctx.lineTo(px, py + 12);
              ctx.stroke();
            }}
          }}
        }}

        function drawTileFloor(x, y, w, h) {{
          ctx.fillStyle = "#334155";
          ctx.fillRect(x, y, w, h);
          ctx.strokeStyle = "#1e293b";
          ctx.lineWidth = 1;
          for (let px = x; px < x + w; px += 16) {{
            ctx.beginPath();
            ctx.moveTo(px, y);
            ctx.lineTo(px, y + h);
            ctx.stroke();
          }}
          for (let py = y; py < y + h; py += 16) {{
            ctx.beginPath();
            ctx.moveTo(x, py);
            ctx.lineTo(x + w, py);
            ctx.stroke();
          }}
        }}

        function drawWall(x, y, w, h) {{
          ctx.fillStyle = "#64748b";
          ctx.fillRect(x, y, w, h);
          // Wall shadow
          ctx.fillStyle = "#475569";
          ctx.fillRect(x, y + h - 4, w, 4);
          ctx.strokeStyle = "#334155";
          ctx.lineWidth = 1;
          ctx.strokeRect(x, y, w, h);
        }}

        // Agents in Smallville RPG Sprite Style
        const alex = {{
          x: 120, y: 140,
          targetX: 350, targetY: 220,
          name: "Alex",
          shirt: "#0284c7",
          hair: "#fde047",
          bubble: "",
          step: 0,
          dir: 1
        }};

        const morgan = {{
          x: 680, y: 310,
          targetX: 450, targetY: 220,
          name: "Morgan",
          shirt: "#dc2626",
          hair: "#1e293b",
          bubble: "",
          step: 0,
          dir: -1
        }};

        let phase = 0;
        let timer = 0;

        function drawSprite(agent) {{
          const {{ x, y, shirt, hair, step }} = agent;
          const bob = Math.sin(step) * 2;

          // Drop shadow
          ctx.fillStyle = "rgba(0,0,0,0.4)";
          ctx.beginPath();
          ctx.ellipse(x, y + 14, 8, 4, 0, 0, Math.PI * 2);
          ctx.fill();

          // Legs / Shoes
          ctx.fillStyle = "#0f172a";
          const legSpread = Math.sin(step * 2) * 3;
          ctx.fillRect(x - 5 + legSpread, y + 8, 4, 6);
          ctx.fillRect(x + 1 - legSpread, y + 8, 4, 6);

          // Body / Suit
          ctx.fillStyle = shirt;
          ctx.fillRect(x - 6, y - 2 + bob, 12, 11);

          // Tie
          ctx.fillStyle = "#ffffff";
          ctx.fillRect(x - 1, y - 1 + bob, 2, 7);

          // Head
          ctx.fillStyle = "#fed7aa"; // skin
          ctx.fillRect(x - 5, y - 12 + bob, 10, 10);

          // Hair
          ctx.fillStyle = hair;
          ctx.fillRect(x - 6, y - 15 + bob, 12, 5);
          ctx.fillRect(x - 6, y - 12 + bob, 2, 4);

          // Smallville-style Tag Bubble: [AL: ⚖️]
          if (agent.bubble) {{
            const bubbleWidth = Math.min(240, agent.bubble.length * 6.5 + 24);
            const bx = Math.max(10, Math.min(canvas.width - bubbleWidth - 10, x - bubbleWidth / 2));
            const by = y - 48 + bob;

            // White Pixel Box with Black Border
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(bx, by, bubbleWidth, 24);
            ctx.strokeStyle = "#000000";
            ctx.lineWidth = 2;
            ctx.strokeRect(bx, by, bubbleWidth, 24);

            // Bubble Tail
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.moveTo(x - 4, by + 24);
            ctx.lineTo(x, by + 30);
            ctx.lineTo(x + 4, by + 24);
            ctx.fill();
            ctx.strokeStyle = "#000000";
            ctx.beginPath();
            ctx.moveTo(x - 4, by + 24);
            ctx.lineTo(x, by + 30);
            ctx.lineTo(x + 4, by + 24);
            ctx.stroke();

            // Bubble Text
            ctx.fillStyle = "#000000";
            ctx.font = "bold 10px monospace";
            const tag = agent === alex ? "AL: " : "MO: ";
            const snippet = agent.bubble.length > 25 ? agent.bubble.substring(0, 23) + "..." : agent.bubble;
            ctx.fillText(tag + snippet, bx + 6, by + 16);
          }}
        }}

        function moveAgent(agent) {{
          const dx = agent.targetX - agent.x;
          const dy = agent.targetY - agent.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist > 2) {{
            agent.x += (dx / dist) * 1.5;
            agent.y += (dy / dist) * 1.5;
            agent.step += 0.2;
            return false;
          }} else {{
            agent.x = agent.targetX;
            agent.y = agent.targetY;
            agent.step = 0;
            return true;
          }}
        }}

        function drawMap() {{
          // Outside courtyard grass
          ctx.fillStyle = "#4ade80";
          ctx.fillRect(0, 0, canvas.width, canvas.height);

          // Outer walls
          drawWall(20, 20, 760, 16);
          drawWall(20, 380, 760, 16);
          drawWall(20, 20, 16, 376);
          drawWall(764, 20, 16, 376);

          // Room 1: Research Library (Left)
          drawWoodFloor(36, 36, 220, 344);
          drawWall(256, 36, 12, 130);
          drawWall(256, 230, 12, 150); // doorway at 166-230

          // Room 2: Main Conference & Negotiation Hall (Center)
          drawTileFloor(268, 36, 260, 344);
          drawWall(528, 36, 12, 130);
          drawWall(528, 230, 12, 150); // doorway

          // Room 3: Opposing Counsel Chambers (Right)
          drawWoodFloor(540, 36, 224, 344);

          // Room Labels
          ctx.fillStyle = "#cbd5e1";
          ctx.font = "bold 10px monospace";
          ctx.fillText("📚 LAW LIBRARY", 50, 56);
          ctx.fillText("⚖️ NEGOTIATION SUITE", 330, 56);
          ctx.fillText("💼 OPPOSING OFFICE", 580, 56);

          // Furniture: Bookshelves in Library
          ctx.fillStyle = "#78350f";
          for (let by = 70; by < 330; by += 50) {{
            ctx.fillRect(50, by, 30, 36);
            ctx.fillStyle = "#fef08a";
            ctx.fillRect(54, by + 4, 22, 6);
            ctx.fillStyle = "#93c5fd";
            ctx.fillRect(54, by + 14, 22, 6);
            ctx.fillStyle = "#f87171";
            ctx.fillRect(54, by + 24, 22, 6);
            ctx.fillStyle = "#78350f";
          }}

          // Furniture: Conference Table & Chairs (Center)
          // Table Rug
          ctx.fillStyle = "#991b1b";
          ctx.fillRect(330, 170, 140, 100);
          ctx.strokeStyle = "#fef08a";
          ctx.lineWidth = 2;
          ctx.strokeRect(330, 170, 140, 100);

          // Oak Conference Table
          ctx.fillStyle = "#b45309";
          ctx.fillRect(350, 190, 100, 60);
          ctx.strokeStyle = "#78350f";
          ctx.lineWidth = 2;
          ctx.strokeRect(350, 190, 100, 60);

          // Papers & Contract on Table
          ctx.fillStyle = "#ffffff";
          ctx.fillRect(380, 205, 14, 18);
          ctx.fillStyle = "#000000";
          ctx.fillRect(383, 209, 8, 2);
          ctx.fillRect(383, 213, 8, 2);
          ctx.fillRect(383, 217, 8, 2);

          // Chairs
          ctx.fillStyle = "#1e293b";
          ctx.fillRect(330, 205, 14, 30); // Alex chair
          ctx.fillRect(456, 205, 14, 30); // Morgan chair

          // Furniture: Opposing Desk
          ctx.fillStyle = "#475569";
          ctx.fillRect(600, 120, 90, 44);
          ctx.fillStyle = "#0284c7";
          ctx.fillRect(630, 130, 16, 12); // laptop

          // Indoor Plants
          ctx.fillStyle = "#15803d";
          ctx.beginPath();
          ctx.arc(280, 70, 10, 0, Math.PI * 2);
          ctx.arc(516, 70, 10, 0, Math.PI * 2);
          ctx.fill();
        }}

        function loop() {{
          drawMap();

          const alexReady = moveAgent(alex);
          const morganReady = moveAgent(morgan);

          drawSprite(alex);
          drawSprite(morgan);

          if (phase === 0) {{
            activityLabel.innerText = "🚶 EN ROUTE TO NEGOTIATION SUITE";
            alex.bubble = "Gathering legal precedents...";
            morgan.bubble = "Reviewing clause demands...";
            if (alexReady && morganReady) {{
              phase = 1;
              timer = 0;
            }}
          }} else if (phase === 1) {{
            activityLabel.innerText = "🗣️ ALEX CHALLENGING UNFAIR TERMS";
            alex.bubble = dialogues[0].text;
            morgan.bubble = "";
            dialogueFeed.innerHTML = '<span class="speaker-tag" style="background:#0369a1;color:#fff;">ALEX:</span> ' + dialogues[0].text;
            timer++;
            if (timer > 200) {{
              phase = 2;
              timer = 0;
            }}
          }} else if (phase === 2) {{
            activityLabel.innerText = "🗣️ MORGAN OFFERING COUNTER-DEFENSE";
            alex.bubble = "";
            morgan.bubble = dialogues[1].text;
            dialogueFeed.innerHTML = '<span class="speaker-tag" style="background:#b91c1c;color:#fff;">MORGAN:</span> ' + dialogues[1].text;
            timer++;
            if (timer > 200) {{
              phase = 3;
              timer = 0;
            }}
          }} else if (phase === 3) {{
            activityLabel.innerText = "🤝 FINALIZING PROTECTIVE AGREEMENT";
            alex.bubble = dialogues[2].text;
            morgan.bubble = "";
            dialogueFeed.innerHTML = '<span class="speaker-tag" style="background:#0369a1;color:#fff;">ALEX (COUNTER):</span> ' + dialogues[2].text;
            timer++;
            if (timer > 240) {{
              phase = 4;
            }}
          }} else if (phase === 4) {{
            activityLabel.innerText = "✅ NEGOTIATION REACHED";
            alex.bubble = "Terms finalized.";
            morgan.bubble = "Acknowledged.";
          }}

          requestAnimationFrame(loop);
        }}

        loop();
      </script>
    </body>
    </html>
    """
    return html_code
