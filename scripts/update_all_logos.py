"""
Apex Logistics AI - Universal Logo & Favicon Replacement Script
Updates all HTML pages, CSS files, and widget script with the unified Apex Logistics AI branding.
"""

import os
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

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

def update_file(path, modifier_fn):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = modifier_fn(content)
    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {os.path.relpath(path, FRONTEND_DIR)}")
    else:
        print(f"No changes: {os.path.relpath(path, FRONTEND_DIR)}")

# 1. Update index.html
def update_index(html):
    # Favicon
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v=2">', html)
    # Landing Nav Logo
    old_nav_svg = re.compile(
        r'<div class="landing-logo-icon">\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'<div class="landing-logo-icon">\n                    {APEX_SVG_24}\n                </div>'
    html = old_nav_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "index.html"), update_index)

# 2. Update widget-test.html
def update_widget_test(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="assets/favicon.svg?v=2">', html)
    old_brand_svg = re.compile(
        r'<div class="brand-logo-icon">\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'<div class="brand-logo-icon">\n                {APEX_SVG_24}\n            </div>'
    html = old_brand_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "widget-test.html"), update_widget_test)

# 3. Update admin.html
def update_admin(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">', html)
    old_sidebar_svg = re.compile(
        r'<div class="sidebar-logo">\s*(<!--.*?-->)?\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'<div class="sidebar-logo">\n                        <!-- High-DPI Autonomous Apex Logistics AI Mark -->\n                        {APEX_SVG_24}\n                    </div>'
    html = old_sidebar_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "pages", "admin.html"), update_admin)

# 4. Update client-dashboard.html
def update_client_dash(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">', html)
    old_sidebar_svg = re.compile(
        r'<div class="sidebar-logo">\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'<div class="sidebar-logo">\n                        {APEX_SVG_24}\n                    </div>'
    html = old_sidebar_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "pages", "client-dashboard.html"), update_client_dash)

# 5. Update login.html
def update_login(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">', html)
    # Update gradient in CSS
    html = html.replace(
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #4d148c 0%, #7c3aed 100%)"
    )
    html = html.replace(
        "box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35)",
        "box-shadow: 0 8px 24px rgba(77, 20, 140, 0.45)"
    )
    old_logo_svg = re.compile(
        r'<div class="login-logo-icon">\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'<div class="login-logo-icon">\n                        {APEX_SVG_24}\n                    </div>'
    html = old_logo_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "pages", "login.html"), update_login)

# 6. Update signup.html
def update_signup(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">', html)
    html = html.replace(
        "linear-gradient(135deg, #667eea, #764ba2)",
        "linear-gradient(135deg, #4d148c, #7c3aed)"
    )
    old_brand_svg = re.compile(
        r'<div class="brand-logo-icon">\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'<div class="brand-logo-icon">\n                        {APEX_SVG_24}\n                    </div>'
    html = old_brand_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "pages", "signup.html"), update_signup)

# 7. Update onboarding.html
def update_onboarding(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">', html)
    html = html.replace(
        "linear-gradient(135deg, #667eea, #764ba2)",
        "linear-gradient(135deg, #4d148c, #7c3aed)"
    )
    old_bg_svg = re.compile(
        r'<div class="bg-logo-icon"[^>]*>\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'''<div class="bg-logo-icon" style="width:36px;height:36px;background:linear-gradient(135deg, #4d148c, #7c3aed);border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(124,58,237,0.4);">\n            {APEX_SVG_24}\n        </div>'''
    html = old_bg_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "pages", "onboarding.html"), update_onboarding)

# 8. Update escalations.html, knowledge-base.html, widget-management.html
def update_generic_page(html):
    html = re.sub(r'<link rel="icon"[^>]+>', '<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg?v=2">', html)
    old_sb_svg = re.compile(
        r'<div class="sidebar-logo-icon"[^>]*>\s*<svg[^>]*>.*?</svg>\s*</div>',
        re.DOTALL
    )
    replacement = f'''<div class="sidebar-logo-icon" style="width:36px;height:36px;background:linear-gradient(135deg, #4d148c, #7c3aed);border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(124,58,237,0.4);flex-shrink:0;">\n                        {APEX_SVG_24}\n                    </div>'''
    html = old_sb_svg.sub(replacement, html)
    return html

update_file(os.path.join(FRONTEND_DIR, "pages", "escalations.html"), update_generic_page)
update_file(os.path.join(FRONTEND_DIR, "pages", "knowledge-base.html"), update_generic_page)
update_file(os.path.join(FRONTEND_DIR, "pages", "widget-management.html"), update_generic_page)

# 9. Update embed.js
def update_embed_js(js):
    # Header Avatar replacement
    old_avatar = '<div class="bai-header-avatar">🤖</div>'
    new_avatar = f'''<div class="bai-header-avatar">
          {APEX_SVG_24}
        </div>'''
    js = js.replace(old_avatar, new_avatar)
    
    # Also handle if it had unicode or robot character
    js = re.sub(r'<div class="bai-header-avatar">.*?</div>', new_avatar, js, count=1)
    
    # Also ensure avatar CSS sizes the internal svg properly
    js = js.replace(
        '.bai-header-avatar {',
        '.bai-header-avatar { padding: 4px; box-sizing: border-box;'
    )
    return js

update_file(os.path.join(FRONTEND_DIR, "widget", "embed.js"), update_embed_js)

print("All files processed!")
