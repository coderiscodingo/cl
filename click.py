import asyncio
import random
import string
from playwright.async_api import async_playwright
import sys
from pynput.mouse import Button, Controller
import time

def generate_random_string(length=9):
    """Generate a random string of specified length"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_proxy_config():
    """Generate proxy configuration with random session string"""
    random_session = generate_random_string(9)
    username = f"F7PKJCvU-session-{random_session}"
    password = "NUm0qBvSL7FW"
    
    return {
        "server": "http://gateway.aluvia.io:8080",
        "username": username,
        "password": password
    }

async def click_element_with_mouse(page, element):
    """Use pynput to physically move mouse and click the element"""
    mouse = Controller()
    
    # Get the bounding box of the element (relative to viewport)
    box = await element.bounding_box()
    if box:
        # Add a visual highlight to see where Playwright thinks the element is
        await element.evaluate('''(element) => {
            element.style.border = '3px solid red';
            element.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
        }''')
        await asyncio.sleep(0.5)
        
        # Get the page's viewport position on screen
        viewport_offset = await page.evaluate('''() => {
            return {
                x: window.screenX,
                y: window.screenY,
                innerWidth: window.innerWidth,
                innerHeight: window.innerHeight,
                outerWidth: window.outerWidth,
                outerHeight: window.outerHeight,
                devicePixelRatio: window.devicePixelRatio
            }
        }''')
        
        print(f"Viewport offset: x={viewport_offset['x']}, y={viewport_offset['y']}")
        print(f"Device pixel ratio: {viewport_offset['devicePixelRatio']}")
        
        # Calculate absolute screen position
        # The browser chrome (toolbar, tabs, etc.) height
        chrome_height = viewport_offset['outerHeight'] - viewport_offset['innerHeight']
        
        # Adjust for DPI scaling if needed
        scale_factor = viewport_offset['devicePixelRatio']
        
        # Element position in viewport
        element_x = box['x'] + box['width'] / 2
        element_y = box['y'] + box['height'] / 2
        
        # Calculate absolute position
        # Add viewport offset and account for browser chrome
        x = viewport_offset['x'] + element_x
        y = viewport_offset['y'] + element_y + chrome_height
        
        print(f"Element viewport position: x={element_x}, y={element_y}")
        print(f"Browser chrome height: {chrome_height}")
        print(f"Calculated screen position: x={x}, y={y}")
        
        # Move mouse in small steps for better accuracy
        current_pos = mouse.position
        print(f"Current mouse position: {current_pos}")
        
        # Move to position with slight delay
        mouse.position = (x, y)
        await asyncio.sleep(0.3)  # Wait for mouse to arrive
        
        # Verify position
        final_pos = mouse.position
        print(f"Final mouse position: {final_pos}")
        
        # Click
        mouse.click(Button.left, 1)
        print("Clicked!")
        
        return True
    return False

async def human_like_interaction(page, duration_seconds):
    """Perform human-like mouse movements and scrolling for specified duration"""
    mouse = Controller()
    
    # Get viewport dimensions
    viewport_offset = await page.evaluate('''() => {
        return {
            x: window.screenX,
            y: window.screenY,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            outerHeight: window.outerHeight,
            scrollY: window.scrollY,
            documentHeight: document.body.scrollHeight
        }
    }''')
    
    chrome_height = viewport_offset['outerHeight'] - viewport_offset['innerHeight']
    
    print(f"\n🖱️ Starting human-like interaction for {duration_seconds} seconds...")
    
    start_time = time.time()
    action_count = 0
    
    while time.time() - start_time < duration_seconds:
        action_type = random.choice(['hover', 'scroll', 'pause'])
        
        if action_type == 'hover':
            # Move mouse to random position within viewport
            target_x = viewport_offset['x'] + random.randint(100, viewport_offset['innerWidth'] - 100)
            target_y = viewport_offset['y'] + random.randint(100, viewport_offset['innerHeight'] - 100) + chrome_height
            
            # Move in small steps for human-like movement
            current_x, current_y = mouse.position
            steps = random.randint(5, 15)
            
            for step in range(steps):
                progress = (step + 1) / steps
                # Add slight randomness to path
                intermediate_x = current_x + (target_x - current_x) * progress + random.randint(-10, 10)
                intermediate_y = current_y + (target_y - current_y) * progress + random.randint(-10, 10)
                mouse.position = (intermediate_x, intermediate_y)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            action_count += 1
            print(f"  📍 Action {action_count}: Moved mouse to ({target_x:.0f}, {target_y:.0f})")
            
            # Sometimes pause after moving
            if random.random() < 0.3:
                pause_time = random.uniform(0.5, 2)
                await asyncio.sleep(pause_time)
                
        elif action_type == 'scroll':
            # Scroll up or down randomly
            scroll_direction = random.choice(['up', 'down'])
            scroll_amount = random.randint(100, 500)
            
            # Ensure mouse is in viewport for scrolling
            center_x = viewport_offset['x'] + viewport_offset['innerWidth'] / 2
            center_y = viewport_offset['y'] + viewport_offset['innerHeight'] / 2 + chrome_height
            mouse.position = (center_x, center_y)
            await asyncio.sleep(0.1)
            
            # Perform scrolling in chunks
            scroll_clicks = scroll_amount // 120
            direction = -1 if scroll_direction == 'down' else 1
            
            for _ in range(scroll_clicks):
                mouse.scroll(0, direction)
                await asyncio.sleep(random.uniform(0.01, 0.03))
            
            action_count += 1
            print(f"  📜 Action {action_count}: Scrolled {scroll_direction} {scroll_amount}px")
            
            # Sometimes pause after scrolling
            if random.random() < 0.4:
                pause_time = random.uniform(0.5, 1.5)
                await asyncio.sleep(pause_time)
                
        else:  # pause
            pause_time = random.uniform(0.3, 1.5)
            print(f"  ⏸️  Pausing for {pause_time:.1f} seconds...")
            await asyncio.sleep(pause_time)
    
    print(f"✅ Human-like interaction completed! Performed {action_count} actions in {duration_seconds} seconds")

async def scroll_page_with_mouse(page):
    """Scroll the page using pynput mouse wheel"""
    mouse = Controller()
    
    # Get viewport center for mouse position
    viewport_offset = await page.evaluate('''() => {
        return {
            x: window.screenX,
            y: window.screenY,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            outerHeight: window.outerHeight
        }
    }''')
    
    chrome_height = viewport_offset['outerHeight'] - viewport_offset['innerHeight']
    
    # Position mouse in the center of the viewport
    center_x = viewport_offset['x'] + viewport_offset['innerWidth'] / 2
    center_y = viewport_offset['y'] + viewport_offset['innerHeight'] / 2 + chrome_height
    
    mouse.position = (center_x, center_y)
    await asyncio.sleep(0.2)
    
    # Generate random scroll amount (between 300 and 800 pixels)
    scroll_amount = random.randint(300, 800)
    print(f"Scrolling down {scroll_amount} pixels...")
    
    # Scroll down using mouse wheel
    scroll_clicks = scroll_amount // 120
    
    for _ in range(scroll_clicks):
        mouse.scroll(0, -1)  # Negative for scroll down
        await asyncio.sleep(0.01)  # Small delay between scrolls
    
    print(f"Scrolled down {scroll_amount} pixels")
    return True

def is_blacklisted(style, onclick, href):
    """Check if an element is blacklisted (contains /1/ in URL)"""
    blacklist_pattern = "/1/"
    
    if style and blacklist_pattern in style:
        return True
    if onclick and blacklist_pattern in onclick:
        return True
    if href and blacklist_pattern in href:
        return True
    
    return False

def is_valid_target(style, onclick, href):
    """Check if element is a valid target (contains /{anything}/{anything} but not /1/{anything})"""
    import re
    
    # Check all attributes for URL patterns
    attributes = [attr for attr in [style, onclick, href] if attr]
    
    for attr in attributes:
        # Look for URLs containing /{something}/{something}
        # Pattern: /{number}/{something} or /{number}/{number}
        matches = re.findall(r'/(\d+)/', attr)
        for match in matches:
            # If it's not /1/, it's valid
            if match != '1':
                return True
    
    return False

async def find_and_click_target(page):
    """Find the target element and click it with priority order"""
    # Priority 1: Specific JPG image
    target_image_jpg = "8a2c9604546315d5c98557dead3c48d4"
    # Priority 2: Specific GIF image  
    target_image_gif = "15bcac895abba24f329e2819e34f4775"
    
    try:
        print("Waiting for target element to appear...")
        
        # Wait a bit for dynamic content
        await asyncio.sleep(3)
        
        target_element = None
        selected_priority = None
        
        for attempt in range(10):  # Only 10 attempts
            # DUMP ALL PAGE CONTENT FOR DEBUGGING
            if attempt == 0 or attempt % 3 == 0:
                print(f"\n--- Debug dump at attempt {attempt + 1} ---")
                
                # Search for the image URLs in the entire page HTML
                page_content = await page.content()
                if target_image_jpg in page_content:
                    print(f"✅ Found priority 1 JPG '{target_image_jpg}' in page HTML!")
                if target_image_gif in page_content:
                    print(f"✅ Found priority 2 GIF '{target_image_gif}' in page HTML!")
            
            # Get all anchor elements
            elements = await page.query_selector_all('a')
            
            # PRIORITY 1: Look for the JPG image
            for element in elements:
                style = await element.get_attribute('style')
                onclick = await element.get_attribute('onclick')
                href = await element.get_attribute('href')
                
                # Skip blacklisted elements
                if is_blacklisted(style, onclick, href):
                    continue
                
                # Check for priority 1 (JPG)
                if style and target_image_jpg in style:
                    target_element = element
                    selected_priority = "1 (Specific JPG)"
                    print(f"✅ FOUND PRIORITY 1 ELEMENT (JPG)!")
                    break
            
            if target_element:
                break
            
            # PRIORITY 2: If JPG not found, look for the GIF image
            if not target_element:
                for element in elements:
                    style = await element.get_attribute('style')
                    onclick = await element.get_attribute('onclick')
                    href = await element.get_attribute('href')
                    
                    # Skip blacklisted elements
                    if is_blacklisted(style, onclick, href):
                        continue
                    
                    # Check for priority 2 (GIF)
                    if style and target_image_gif in style:
                        target_element = element
                        selected_priority = "2 (Specific GIF)"
                        print(f"✅ FOUND PRIORITY 2 ELEMENT (GIF)!")
                        break
            
            if target_element:
                break
            
            # PRIORITY 3: If specific targets not found, find any valid element
            if not target_element:
                print("Priority targets not found, looking for any valid element...")
                
                valid_elements = []
                for element in elements:
                    style = await element.get_attribute('style')
                    onclick = await element.get_attribute('onclick')
                    href = await element.get_attribute('href')
                    
                    # Skip blacklisted elements (/1/{anything})
                    if is_blacklisted(style, onclick, href):
                        continue
                    
                    # Check if it's a valid target (/{anything}/{anything} where first is not 1)
                    if is_valid_target(style, onclick, href):
                        valid_elements.append(element)
                
                if valid_elements:
                    # Pick a random valid element
                    target_element = random.choice(valid_elements)
                    selected_priority = "3 (Random valid element)"
                    print(f"✅ FOUND PRIORITY 3 ELEMENT! Selected from {len(valid_elements)} valid elements")
                    break
                else:
                    print(f"Attempt {attempt + 1}/10: No valid targets found, waiting...")
            
            if target_element:
                break
            
            await asyncio.sleep(1)
        
        if target_element:
            print(f"Using priority {selected_priority} element")
            
            # Scroll the element into view
            await target_element.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            
            success = await click_element_with_mouse(page, target_element)
            if success:
                print(f"✅ Successfully clicked target element (Priority {selected_priority})")
                return True
            else:
                print("❌ Failed to click target element")
                return False
        else:
            print("\n❌ No valid target element found after 10 attempts")
            print("Restarting browser...")
            
    except Exception as e:
        print(f"Error finding/clicking element: {e}")
        import traceback
        traceback.print_exc()
    
    return False

async def main():
    while True:
        proxy_config = get_proxy_config()
        
        print(f"\n{'='*60}")
        print(f"Starting browser with session: {proxy_config['username']}")
        print(f"{'='*60}")
        
        async with async_playwright() as p:
            # Launch browser with proxy settings
            browser = await p.chromium.launch(
                headless=False,
                proxy={
                    "server": proxy_config["server"],
                    "username": proxy_config["username"],
                    "password": proxy_config["password"]
                },
                args=['--ignore-certificate-errors']
            )
            
            # Create context
            context = await browser.new_context()
            
            # Track pages and tabs
            pages = []
            main_page = None
            new_tab = None
            
            # Event handler for new pages
            async def handle_new_page(page):
                nonlocal new_tab, main_page
                if len(pages) > 0:  # Not the first page
                    print(f"New tab opened with URL: {page.url}")
                    new_tab = page
                    
                    # Wait for the URL to change from about:blank to something else
                    async def check_url_change():
                        while page.url == 'about:blank':
                            await asyncio.sleep(0.1)
                        print(f"Tab URL changed to: {page.url}")
                        
                        # Close the new tab immediately
                        print("Closing new tab...")
                        await page.close()
                        print("New tab closed!")
                        
                        # Now focus back on main page
                        if main_page:
                            await main_page.bring_to_front()
                            print("Main page is now in focus")
                            
                            # Wait 2 seconds then scroll
                            print("Waiting 2 seconds before scrolling...")
                            await asyncio.sleep(2)
                            
                            # Initial scroll
                            await scroll_page_with_mouse(main_page)
                            print("Initial scrolling completed!")
                            
                            # Now perform human-like interaction for random 40-80 seconds
                            interaction_duration = random.randint(40, 80)
                            await human_like_interaction(main_page, interaction_duration)
                            
                            # Close browser after interaction
                            print("Interaction completed, closing browser...")
                            await browser.close()
                    
                    # Start checking URL in background
                    asyncio.create_task(check_url_change())
                    
                else:
                    # This is the main page
                    main_page = page
                    
                pages.append(page)
            
            # Listen for new pages
            context.on('page', handle_new_page)
            
            # Open initial page
            page = await context.new_page()
            main_page = page
            
            try:
                print("Navigating to fconverter.vipb.top/docx-to-pdf.php...")
                await page.goto('https://fconverter.vipb.top/pdf-to-docx.php', wait_until='networkidle')
                
                # Find and click the target element
                clicked = await find_and_click_target(page)
                
                if clicked:
                    # Keep browser alive until new tab opens and interaction completes
                    while browser.is_connected():
                        await asyncio.sleep(0.5)
                else:
                    print("No clickable element found, closing browser immediately...")
                
            except Exception as e:
                print(f"Error during navigation: {e}")
            finally:
                if browser.is_connected():
                    await browser.close()
        
        print("Browser closed. Reopening immediately with new session...\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript stopped by user")
        sys.exit(0)
