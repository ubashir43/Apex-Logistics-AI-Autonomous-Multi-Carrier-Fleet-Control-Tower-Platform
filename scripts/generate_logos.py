"""
Apex Logistics AI Logo Design & Preview Generator
"""
import os

APEX_SVG_24 = '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="apex-logo-svg">
  <!-- Top Face (Aerial Freight & Apex Diamond) -->
  <path d="M12 2.2L20.5 7L12 11.8L3.5 7L12 2.2Z" fill="#ffffff" fill-opacity="0.95"/>
  <!-- Top Face Velocity Chevron (Apex Delta) -->
  <path d="M12 4.5L16.5 7.1L12 9.7L7.5 7.1L12 4.5Z" fill="#4d148c"/>
  <path d="M12 5.8L14.2 7.1L12 8.4L9.8 7.1L12 5.8Z" fill="#38bdf8"/>

  <!-- Left Face (Enterprise Logistics Freight Base) -->
  <path d="M3.5 8.4L11.2 12.6V21.5L3.5 17.3V8.4Z" fill="#ffffff" fill-opacity="0.75"/>
  <line x1="6" y1="12" x2="8.5" y2="18" stroke="#4d148c" stroke-width="1.1" stroke-dasharray="1.5 1.5"/>

  <!-- Right Face (Autonomous AI Dispatch Intelligence) -->
  <path d="M12.8 12.6L20.5 8.4V17.3L12.8 21.5V12.6Z" fill="#ffffff" fill-opacity="0.52"/>
  <line x1="18" y1="12" x2="15.5" y2="18" stroke="#38bdf8" stroke-width="1.1" stroke-dasharray="1.5 1.5"/>

  <!-- Center Telemetry Beacon (Quantum AI Route Node) -->
  <circle cx="12" cy="12.2" r="2.2" fill="#38bdf8"/>
  <circle cx="12" cy="12.2" r="1.1" fill="#ffffff"/>

  <!-- Route Waypoint Milestone Blips -->
  <circle cx="3.5" cy="17.3" r="1.2" fill="#10b981"/>
  <circle cx="20.5" cy="17.3" r="1.2" fill="#38bdf8"/>
  <circle cx="12" cy="2.2" r="1.2" fill="#f59e0b"/>
</svg>'''

FAVICON_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <defs>
    <!-- Background Gradient: Deep Obsidian & FedEx Purple Brand Base -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b071e"/>
      <stop offset="50%" stop-color="#1e103f"/>
      <stop offset="100%" stop-color="#4d148c"/>
    </linearGradient>

    <!-- Top Face: Aerial Satellite Telemetry & Global Air Freight -->
    <linearGradient id="topFace" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
    
    <!-- Left Face: Apex Enterprise Ground Logistics (FedEx Purple Signature) -->
    <linearGradient id="leftFace" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#7c3aed"/>
      <stop offset="100%" stop-color="#4d148c"/>
    </linearGradient>

    <!-- Right Face: Autonomous AI Predictive Neural Network -->
    <linearGradient id="rightFace" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#a855f7"/>
      <stop offset="100%" stop-color="#6d28d9"/>
    </linearGradient>

    <!-- Neon Glow Filter -->
    <filter id="coreGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>

    <!-- Drop Shadow -->
    <filter id="cubeShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Container Box with Rounded Chamfer -->
  <rect width="64" height="64" rx="16" fill="url(#bgGrad)"/>
  <rect width="64" height="64" rx="16" stroke="rgba(255,255,255,0.18)" stroke-width="1.2"/>

  <!-- Orbital Radar Telemetry Rings -->
  <circle cx="32" cy="32" r="25" stroke="#38bdf8" stroke-width="1" stroke-dasharray="3 5" opacity="0.35"/>
  <circle cx="32" cy="32" r="17" stroke="#c084fc" stroke-width="0.8" stroke-dasharray="2 3" opacity="0.3"/>

  <!-- Autonomous Apex 3D Freight Cube -->
  <g filter="url(#cubeShadow)">
    <!-- Top Face: Apex Diamond / Aerial Prism -->
    <polygon points="32,10 49,19.5 32,29 15,19.5" fill="url(#topFace)"/>
    <!-- Top Face Dynamic Inner Apex Arrow (Pointing Forward & Upward) -->
    <polygon points="32,14 43,20 32,26 21,20" fill="#ffffff" fill-opacity="0.9"/>
    <polygon points="32,17 39,21 32,24.5 25,21" fill="url(#topFace)"/>

    <!-- Left Face: Enterprise Logistics Ground Module -->
    <polygon points="15,21.5 30.5,30 30.5,50 15,41.5" fill="url(#leftFace)"/>
    <!-- Left Face Neural Telemetry Route -->
    <line x1="18" y1="26" x2="27.5" y2="44.5" stroke="#a78bfa" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.85"/>

    <!-- Right Face: Autonomous AI Dispatch Module -->
    <polygon points="33.5,30 49,21.5 49,41.5 33.5,50" fill="url(#rightFace)"/>
    <!-- Right Face Neural Telemetry Route -->
    <line x1="46" y1="26" x2="36.5" y2="44.5" stroke="#38bdf8" stroke-width="1.2" stroke-linecap="round" stroke-dasharray="2 3" opacity="0.85"/>
  </g>

  <!-- Central Telemetry Beacon (Quantum AI Route Node) -->
  <g filter="url(#coreGlow)">
    <circle cx="32" cy="29.8" r="3.5" fill="#ffffff"/>
    <circle cx="32" cy="29.8" r="2" fill="#06b6d4"/>
  </g>

  <!-- Route Milestone Telemetry Blips -->
  <circle cx="15" cy="41.5" r="2" fill="#10b981"/>
  <circle cx="49" cy="41.5" r="2" fill="#38bdf8"/>
  <circle cx="32" cy="10" r="1.8" fill="#f59e0b"/>
</svg>'''

# Save the favicon.svg
favicon_path = os.path.join("behavioral-agentic-ai", "frontend", "assets", "favicon.svg")
with open(favicon_path, "w", encoding="utf-8") as f:
    f.write(FAVICON_SVG)
print("Updated:", favicon_path)

# Generate HTML Preview
preview_html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Apex Logistics AI - Logo & Favicon Verification</title>
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v=2">
<style>
body {{
  background: #0b071e;
  color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 30px;
  align-items: center;
}}
.card {{
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 24px;
}}
.logo-container {{
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #4d148c 0%, #7c3aed 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(124,58,237,0.4);
}}
.logo-container svg {{
  width: 26px;
  height: 26px;
}}
.brand-name {{
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}}
.favicon-img {{
  width: 64px;
  height: 64px;
  border-radius: 16px;
  box-shadow: 0 0 24px rgba(77,20,140,0.6);
}}
</style>
</head>
<body>
  <h1>Apex Logistics AI - Logo & Favicon Assets</h1>
  
  <div class="card">
    <img src="assets/favicon.svg?v=2" class="favicon-img" alt="Favicon" />
    <div>
      <div class="brand-name">Favicon Asset (64x64 High-DPI)</div>
      <div style="color: #a78bfa; font-size: 0.9rem;">Loaded directly from assets/favicon.svg</div>
    </div>
  </div>

  <div class="card">
    <div class="logo-container">
      {APEX_SVG_24}
    </div>
    <div>
      <div class="brand-name">Apex Logistics AI</div>
      <div style="color: #38bdf8; font-size: 0.9rem;">Vector Brandmark for Headers, Sidebars & Auth</div>
    </div>
  </div>
</body>
</html>'''

preview_path = os.path.join("behavioral-agentic-ai", "frontend", "logo-preview.html")
with open(preview_path, "w", encoding="utf-8") as f:
    f.write(preview_html)
print("Updated:", preview_path)
