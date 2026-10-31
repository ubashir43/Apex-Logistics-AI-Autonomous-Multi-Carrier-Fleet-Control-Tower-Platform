# -*- coding: utf-8 -*-
"""
Capture complete Fig 13 conversation and live dashboard screenshots.
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

FIGURES_DIR = r"D:\Logistics Research\Paper2\figures"
os.makedirs(FIGURES_DIR, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,2400")
chrome_options.add_argument("--force-device-scale-factor=2")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)

try:
    print("Navigating to widget-test.html...")
    driver.get("http://localhost:5500/widget-test.html")
    time.sleep(2)

    # 1. Expand panel to show all 6 turns without scroll clipping
    driver.execute_script("""
        const host = document.getElementById('apex-logistics-ai-widget');
        const root = host.shadowRoot;
        const panel = root.querySelector('.bai-panel');
        const msgs = root.querySelector('#bai-msgs');
        
        // Open panel
        panel.classList.add('open');
        
        // Expand styling so all turns are rendered in full height
        panel.style.position = 'relative';
        panel.style.height = 'auto';
        panel.style.maxHeight = 'none';
        panel.style.width = '460px';
        panel.style.bottom = 'auto';
        panel.style.right = 'auto';
        panel.style.boxShadow = '0 20px 60px rgba(0,0,0,0.3)';
        
        msgs.style.height = 'auto';
        msgs.style.maxHeight = 'none';
        msgs.style.overflow = 'visible';
    """)
    time.sleep(2)

    host_elem = driver.find_element(By.ID, "apex-logistics-ai-widget")
    shadow_root = host_elem.shadow_root
    panel_elem = shadow_root.find_element(By.CSS_SELECTOR, ".bai-panel")
    
    fig13_full_chat_path = os.path.join(FIGURES_DIR, "fig13_live_chat_information_retrieval.png")
    panel_elem.screenshot(fig13_full_chat_path)
    print(f"Saved complete 6-turn chat panel to: {fig13_full_chat_path}")

    # Also capture normal floating widget view for full page
    driver.get("http://localhost:5500/widget-test.html")
    time.sleep(2)
    driver.execute_script("""
        const host = document.getElementById('apex-logistics-ai-widget');
        const root = host.shadowRoot;
        const bubble = root.querySelector('.bai-bubble');
        const panel = root.querySelector('.bai-panel');
        if (bubble && panel && !panel.classList.contains('open')) {
            bubble.click();
        }
    """)
    time.sleep(2)
    fig13_page_path = os.path.join(FIGURES_DIR, "fig13_live_chat_full_page.png")
    driver.save_screenshot(fig13_page_path)
    print(f"Saved live page context to: {fig13_page_path}")

    # ==========================================
    # 2. Control Tower Dashboard (Fig 11 / Fig 9 UI)
    # ==========================================
    driver.set_window_size(1920, 1080)
    driver.get("http://localhost:5500/pages/client-dashboard.html#logistics")
    time.sleep(1)
    driver.execute_script("""
        localStorage.setItem('bai_auth_token', 'demo-token');
        localStorage.setItem('bai_current_tenant', JSON.stringify({
            id: 2,
            name: 'Apex Logistics Copilot',
            widget_api_key: 'wk_r_8L9yRpFHZBowcT2EMR-4ZgJRSzhVH6qsLt1pJOl2Y'
        }));
    """)
    driver.get("http://localhost:5500/pages/client-dashboard.html#logistics")
    time.sleep(3)

    fig11_path = os.path.join(FIGURES_DIR, "fig11_control_tower_uncertainty_telemetry.png")
    driver.save_screenshot(fig11_path)
    print(f"Saved Fig 11 / Control Tower logistics to: {fig11_path}")

    # Fig 9 Live Control Tower overview
    driver.get("http://localhost:5500/pages/client-dashboard.html#overview")
    time.sleep(3)
    fig9_ui_path = os.path.join(FIGURES_DIR, "fig9_live_control_tower_overview.png")
    driver.save_screenshot(fig9_ui_path)
    print(f"Saved Fig 9 live overview to: {fig9_ui_path}")

finally:
    driver.quit()
    print("All screenshots successfully captured!")
