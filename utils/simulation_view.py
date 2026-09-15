import json

def get_office_simulation_html(msg1: str = "", msg2: str = "", msg3: str = "") -> str:
    """
    Renders an exact Smallville-style Generative Agents layout:
    - Overview map with law firm rooms, pathways, and green courtyards.
    - Floating Picture-in-Picture Callout Cards with leader lines and pins.
    - Close-up room scenes showing pixel characters with speech bubbles and dialogue scripts.
    """
    clean_msg1 = (msg1.strip() if msg1 else "Section 4.2 imposes unlimited unilateral liability on the user. We demand mutual indemnification or a $5,000 liability cap.")
    clean_msg2 = (msg2.strip() if msg2 else "Our client requires indemnity protection for operational disputes, but we can agree to cap liability at two months of service fees.")
    clean_msg3 = (msg3.strip() if msg3 else "We accept the two-month fee cap, provided that the 90-day auto-renewal notice period is reduced to 30 days.")

    safe_msg1 = json.dumps(clean_msg1)
    safe_msg2 = json.dumps(clean_msg2)
    safe_msg3 = json.dumps(clean_msg3)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace, sans-serif; }}
        body {{
          background: #0f172a;
          color: #f8fafc;
          padding: 8px;
          display: flex;
          justify-content: center;
          align-items: center;
        }}
        #canvas-stage {{
          position: relative;
          width: 900px;
          height: 600px;
          background: #86efac; /* Smallville-style grass green */
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 16px 40px rgba(0,0,0,0.6);
          border: 3px solid #334155;
        }}
        
        /* Map Canvas */
        #mapCanvas {{
          position: absolute;
          top: 0; left: 0;
          width: 900px; height: 600px;
          image-rendering: pixelated;
        }}

        /* Leader Lines SVG */
        #leaderSvg {{
          position: absolute;
          top: 0; left: 0;
          width: 900px; height: 600px;
          pointer-events: none;
          z-index: 10;
        }}

        /* Floating Smallville Callout Cards */
        .callout-card {{
          position: absolute;
          background: rgba(30, 41, 59, 0.95);
          border: 3px solid #64748b;
          border-radius: 8px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.6);
          overflow: hidden;
          z-index: 20;
          display: flex;
          flex-direction: column;
        }}
        .card-header {{
          background: #475569;
          color: #ffffff;
          padding: 5px 10px;
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.3px;
        }}
        .card-viewport {{
          width: 100%;
          height: 70px;
          background: #1e293b;
          position: relative;
          border-bottom: 2px solid #334155;
          image-rendering: pixelated;
        }}
        .card-dialogue {{
          background: #ffffff;
          color: #0f172a;
          padding: 8px 12px;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          font-size: 11px;
          line-height: 1.45;
          max-height: 130px;
          overflow-y: auto;
        }}
        .card-dialogue::-webkit-scrollbar {{
          width: 5px;
        }}
        .card-dialogue::-webkit-scrollbar-thumb {{
          background: #94a3b8;
          border-radius: 3px;
        }}

        /* Specific Card Positions */
        #card-library {{
          top: 20px; left: 20px;
          width: 250px;
        }}
        #card-opposing {{
          top: 20px; right: 20px;
          width: 250px;
        }}
        #card-negotiation {{
          bottom: 16px; left: 160px;
          width: 580px;
        }}

        /* Pixel Speech Bubble */
        .pixel-bubble {{
          position: absolute;
          background: #ffffff;
          color: #000000;
          border: 2px solid #000000;
          padding: 2px 6px;
          font-size: 9px;
          font-family: monospace;
          font-weight: bold;
          border-radius: 2px;
          pointer-events: none;
        }}
      </style>
    </head>
    <body>
      <div id="canvas-stage">
        <!-- Base Map -->
        <canvas id="mapCanvas" width="900" height="560"></canvas>

        <!-- Leader Lines -->
        <svg id="leaderSvg">
          <!-- Library leader line -->
          <line x1="150" y1="185" x2="220" y2="280" stroke="#60a5fa" stroke-width="2.5" stroke-dasharray="4,4" />
          <circle cx="220" cy="280" r="5" fill="#3b82f6" stroke="#ffffff" stroke-width="2" />

          <!-- Opposing leader line -->
          <line x1="750" y1="185" x2="680" y2="280" stroke="#f87171" stroke-width="2.5" stroke-dasharray="4,4" />
          <circle cx="680" cy="280" r="5" fill="#ef4444" stroke="#ffffff" stroke-width="2" />

          <!-- Negotiation table leader line -->
          <line x1="450" y1="440" x2="450" y2="300" stroke="#facc15" stroke-width="2.5" stroke-dasharray="4,4" />
          <circle cx="450" cy="300" r="6" fill="#eab308" stroke="#ffffff" stroke-width="2" />
        </svg>

        <!-- CARD 1: Law Library -->
        <div class="callout-card" id="card-library">
          <div class="card-header">Researching in Law Library</div>
          <canvas class="card-viewport" id="vpLibrary" width="250" height="70"></canvas>
          <div class="card-dialogue">
            <strong style="color: #0369a1;">[Alex]:</strong> Analyzing contract liabilities against consumer protection & Fair Contract Standards...
          </div>
        </div>

        <!-- CARD 2: Opposing Chambers -->
        <div class="callout-card" id="card-opposing">
          <div class="card-header">Opposing Counsel Chambers</div>
          <canvas class="card-viewport" id="vpOpposing" width="250" height="70"></canvas>
          <div class="card-dialogue">
            <strong style="color: #b91c1c;">[Morgan]:</strong> Preparing defense arguments and evaluating client's liability exposure...
          </div>
        </div>

        <!-- CARD 3: Negotiation at Conference Table -->
        <div class="callout-card" id="card-negotiation">
          <div class="card-header">Active Negotiation at Settlement Table</div>
          <canvas class="card-viewport" id="vpConference" width="580" height="70"></canvas>
          <div class="card-dialogue" id="live-nego-text">
            <div style="margin-bottom: 6px;"><strong style="color: #0369a1;">[Alex - Your Counsel]:</strong> {clean_msg1}</div>
            <div style="margin-bottom: 6px;"><strong style="color: #b91c1c;">[Morgan - Opposing]:</strong> {clean_msg2}</div>
            <div><strong style="color: #15803d;">[Alex - Counter-Offer]:</strong> {clean_msg3}</div>
          </div>
        </div>
      </div>

      <script>
        // --- 1. DRAW OVERVIEW MAP ---
        const mapCanvas = document.getElementById('mapCanvas');
        const mctx = mapCanvas.getContext('2d');
        mctx.imageSmoothingEnabled = false;

        function drawOverviewMap() {{
          // Green Field Background
          mctx.fillStyle = "#86efac";
          mctx.fillRect(0, 0, 900, 600);

          // Path / Dirt Road
          mctx.fillStyle = "#fde047";
          mctx.fillRect(80, 240, 740, 70);
          mctx.fillRect(410, 160, 80, 240);

          // Stones / Path Texture
          mctx.fillStyle = "#facc15";
          for (let i = 0; i < 900; i += 30) {{
            mctx.fillRect(i, 250 + (i % 20), 4, 4);
          }}

          // Trees in courtyard
          function drawTree(tx, ty) {{
            mctx.fillStyle = "#15803d";
            mctx.beginPath();
            mctx.arc(tx, ty, 16, 0, Math.PI * 2);
            mctx.fill();
            mctx.fillStyle = "#166534";
            mctx.beginPath();
            mctx.arc(tx - 3, ty - 3, 10, 0, Math.PI * 2);
            mctx.fill();
          }}
          drawTree(120, 190); drawTree(180, 170); drawTree(720, 190); drawTree(780, 170);
          drawTree(120, 370); drawTree(160, 420); drawTree(730, 390); drawTree(770, 430);

          // Building 1: Law Library (Left)
          drawBuilding(mctx, 160, 220, 130, 110, "📚 LAW LIBRARY", "#ca8a04");

          // Building 2: Mediation Center (Center)
          drawBuilding(mctx, 370, 200, 160, 130, "⚖️ MEDIATION HALL", "#b45309");

          // Building 3: Opposing Chambers (Right)
          drawBuilding(mctx, 610, 220, 130, 110, "💼 OPPOSING FIRM", "#475569");
        }}

        function drawBuilding(ctx, bx, by, bw, bh, label, roofColor) {{
          // Roof
          ctx.fillStyle = roofColor;
          ctx.fillRect(bx, by, bw, 32);
          ctx.strokeStyle = "#1e293b";
          ctx.lineWidth = 2;
          ctx.strokeRect(bx, by, bw, 32);

          // Floor / Walls
          ctx.fillStyle = "#f1f5f9";
          ctx.fillRect(bx, by + 32, bw, bh - 32);
          ctx.strokeRect(bx, by + 32, bw, bh - 32);

          // Door
          ctx.fillStyle = "#78350f";
          ctx.fillRect(bx + bw / 2 - 10, by + bh - 24, 20, 24);

          // Window
          ctx.fillStyle = "#38bdf8";
          ctx.fillRect(bx + 16, by + 44, 20, 20);
          ctx.fillRect(bx + bw - 36, by + 44, 20, 20);

          // Label
          ctx.fillStyle = "#0f172a";
          ctx.font = "bold 9px monospace";
          ctx.fillText(label, bx + 12, by + 20);
        }}

        // --- 2. VIEWPORT 1: LIBRARY ZOOM ---
        const vpLib = document.getElementById('vpLibrary');
        const lctx = vpLib.getContext('2d');
        lctx.imageSmoothingEnabled = false;

        function renderLibraryView() {{
          // Wood Floor
          lctx.fillStyle = "#a16207";
          lctx.fillRect(0, 0, 250, 75);
          for (let y = 0; y < 75; y += 12) {{
            lctx.strokeStyle = "#854d0e";
            lctx.strokeRect(0, y, 250, 12);
          }}
          // Bookshelf
          lctx.fillStyle = "#78350f";
          lctx.fillRect(15, 10, 80, 55);
          lctx.fillStyle = "#fef08a"; lctx.fillRect(20, 16, 70, 8);
          lctx.fillStyle = "#f87171"; lctx.fillRect(20, 30, 70, 8);
          lctx.fillStyle = "#60a5fa"; lctx.fillRect(20, 44, 70, 8);

          // Pixel Character (Alex researching)
          drawPixelSprite(lctx, 130, 48, "#0284c7", "#fde047", "AL: 📚", "#ffffff");
        }}

        // --- 3. VIEWPORT 2: OPPOSING ZOOM ---
        const vpOpp = document.getElementById('vpOpposing');
        const octx = vpOpp.getContext('2d');
        octx.imageSmoothingEnabled = false;

        function renderOpposingView() {{
          // Tile Floor
          octx.fillStyle = "#334155";
          octx.fillRect(0, 0, 250, 75);
          for (let x = 0; x < 250; x += 16) {{
            octx.strokeStyle = "#1e293b";
            octx.strokeRect(x, 0, 16, 75);
          }}
          // Desk
          octx.fillStyle = "#64748b";
          octx.fillRect(150, 20, 80, 40);
          octx.fillStyle = "#0284c7";
          octx.fillRect(170, 28, 18, 12); // laptop

          // Pixel Character (Morgan reviewing)
          drawPixelSprite(octx, 100, 48, "#dc2626", "#1e293b", "MO: 💼", "#ffffff");
        }}

        // --- 4. VIEWPORT 3: SETTLEMENT TABLE ZOOM ---
        const vpConf = document.getElementById('vpConference');
        const cctx = vpConf.getContext('2d');
        cctx.imageSmoothingEnabled = false;

        let animStep = 0;
        function renderConferenceView() {{
          cctx.clearRect(0, 0, 480, 85);

          // Carpet
          cctx.fillStyle = "#881337";
          cctx.fillRect(0, 0, 480, 85);
          cctx.strokeStyle = "#facc15";
          cctx.lineWidth = 2;
          cctx.strokeRect(10, 8, 460, 69);

          // Conference Table
          cctx.fillStyle = "#b45309";
          cctx.fillRect(170, 22, 140, 42);
          cctx.strokeStyle = "#78350f";
          cctx.strokeRect(170, 22, 140, 42);

          // Contract on Table
          cctx.fillStyle = "#ffffff";
          cctx.fillRect(230, 32, 18, 22);
          cctx.fillStyle = "#0f172a";
          cctx.fillRect(233, 36, 12, 2);
          cctx.fillRect(233, 40, 12, 2);
          cctx.fillRect(233, 44, 12, 2);

          // Chairs
          cctx.fillStyle = "#1e293b";
          cctx.fillRect(135, 28, 16, 30);
          cctx.fillRect(328, 28, 16, 30);

          // Alex & Morgan sitting across each other with bobbing animation
          const bobA = Math.sin(animStep) * 2;
          const bobM = Math.sin(animStep + Math.PI) * 2;

          drawPixelSprite(cctx, 140, 48 + bobA, "#0284c7", "#fde047", "AL: ⚖️", "#ffffff");
          drawPixelSprite(cctx, 332, 48 + bobM, "#dc2626", "#1e293b", "MO: 📝", "#ffffff");

          animStep += 0.08;
          requestAnimationFrame(renderConferenceView);
        }}

        // Reusable Pixel Sprite Helper
        function drawPixelSprite(ctx, x, y, suit, hair, tag, tagColor) {{
          // Shadow
          ctx.fillStyle = "rgba(0,0,0,0.3)";
          ctx.beginPath();
          ctx.ellipse(x, y + 10, 8, 4, 0, 0, Math.PI * 2);
          ctx.fill();

          // Legs
          ctx.fillStyle = "#0f172a";
          ctx.fillRect(x - 4, y + 4, 3, 6);
          ctx.fillRect(x + 1, y + 4, 3, 6);

          // Body
          ctx.fillStyle = suit;
          ctx.fillRect(x - 5, y - 6, 10, 10);

          // Head
          ctx.fillStyle = "#fde047";
          ctx.fillRect(x - 4, y - 14, 8, 8);

          // Hair
          ctx.fillStyle = hair;
          ctx.fillRect(x - 5, y - 16, 10, 4);

          // Smallville Tag Box: [AK: ☕]
          ctx.fillStyle = tagColor;
          ctx.fillRect(x - 22, y - 32, 46, 15);
          ctx.strokeStyle = "#000000";
          ctx.lineWidth = 1.5;
          ctx.strokeRect(x - 22, y - 32, 46, 15);

          // Tail
          ctx.fillStyle = tagColor;
          ctx.beginPath();
          ctx.moveTo(x - 2, y - 17);
          ctx.lineTo(x, y - 13);
          ctx.lineTo(x + 2, y - 17);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = "#000000";
          ctx.font = "bold 9px monospace";
          ctx.fillText(tag, x - 18, y - 21);
        }}

        // Initialize All Views
        drawOverviewMap();
        renderLibraryView();
        renderOpposingView();
        renderConferenceView();
      </script>
    </body>
    </html>
    """
    return html
