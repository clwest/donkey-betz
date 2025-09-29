#!/usr/bin/env python
"""
Test the enhanced modal functionality
"""

import asyncio
import websockets
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

async def test_modal_websocket():
    """Test WebSocket connection and data"""
    print("🧪 Testing WebSocket connection...")

    uri = "ws://localhost:8000/ws/income-builder/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")

            # Wait for initial message
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(message)

            print(f"📨 Message type: {data.get('type')}")

            if data.get('type') == 'opportunities_update':
                opportunities = data.get('opportunities', [])
                print(f"✅ Got {len(opportunities)} opportunities!")

                if opportunities:
                    first_opp = opportunities[0]
                    print(f"\n🎯 First opportunity:")
                    print(f"   ID: {first_opp.get('id')}")
                    print(f"   Title: {first_opp.get('title')}")
                    print(f"   Company: {first_opp.get('company')}")
                    print(f"   Source: {first_opp.get('source')}")
                    print(f"   Description: {first_opp.get('description', '')[:100]}...")

                return True
            return False

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

def test_modal_ui():
    """Test the modal UI enhancement"""
    print("\n🖥️  Testing Modal UI...")

    try:
        # Setup Chrome driver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)

        # Navigate to Income Builder
        driver.get("http://localhost:8000/income/")
        print("✅ Page loaded")

        # Wait for opportunities to load
        wait = WebDriverWait(driver, 15)
        opportunities = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "opportunity-card"))
        )
        print(f"✅ Found {len(opportunities)} opportunity cards")

        if opportunities:
            # Click first "View Details" button
            first_card = opportunities[0]
            view_details_btn = first_card.find_element(By.CLASS_NAME, "view-details-btn")

            print(f"🎯 Testing View Details for: {first_card.find_element(By.TAG_NAME, 'h3').text}")
            view_details_btn.click()

            # Wait for modal to appear
            modal = wait.until(
                EC.presence_of_element_located((By.ID, "opportunityModal"))
            )
            print("✅ Modal opened")

            # Check modal content
            modal_title = modal.find_element(By.CLASS_NAME, "modal-title").text
            print(f"✅ Modal title: {modal_title}")

            # Check for info grid
            try:
                info_grid = modal.find_element(By.CLASS_NAME, "info-grid")
                info_items = info_grid.find_elements(By.CLASS_NAME, "info-item")
                print(f"✅ Info grid with {len(info_items)} items")

                for item in info_items[:3]:  # Show first 3 items
                    label = item.find_element(By.CLASS_NAME, "info-label").text
                    value = item.find_element(By.CLASS_NAME, "info-value").text
                    print(f"   {label}: {value}")

            except Exception as e:
                print(f"⚠️  Info grid not found: {e}")

            # Check description
            try:
                description = modal.find_element(By.CLASS_NAME, "job-description").text
                print(f"✅ Description: {description[:100]}...")
            except Exception as e:
                print(f"⚠️  Description not found: {e}")

            # Close modal
            close_btn = modal.find_element(By.CLASS_NAME, "btn-close")
            close_btn.click()
            print("✅ Modal closed")

            driver.quit()
            return True
        else:
            print("❌ No opportunities found")
            driver.quit()
            return False

    except Exception as e:
        print(f"❌ UI test error: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Modal Functionality\n")

    # Test WebSocket connection
    ws_result = await test_modal_websocket()

    # Test UI functionality
    ui_result = test_modal_ui()

    print(f"\n📊 Test Results:")
    print(f"   WebSocket: {'✅ PASS' if ws_result else '❌ FAIL'}")
    print(f"   UI Modal: {'✅ PASS' if ui_result else '❌ FAIL'}")

    overall = ws_result and ui_result
    print(f"\n{'🎉 ALL TESTS PASSED!' if overall else '⚠️  SOME TESTS FAILED'}")

    return overall

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)