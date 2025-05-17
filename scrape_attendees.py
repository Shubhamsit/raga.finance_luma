

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
# import json
# import time
# import random

# def scrape_attendees(driver, event_id, event_type="past"):
#     """
#     Scrape attendees from Luma event with reliable event finding and proven scraping logic
#     Parameters:
#         driver: Selenium WebDriver instance (must be logged in)
#         event_id: ID of the event to scrape
#         event_type: "past" or "upcoming" (default: "upcoming")
#     Returns:
#         dict: Contains event details and attendees list
#     """
#     if not driver:
#         print("Driver not initialized.")
#         return {
#             'event_name': "Unknown Event",
#             'event_date': "Date not found",
#             'event_time': "Time not found",
#             'event_location': "Location not found",
#             'attendees': []
#         }

#     attendees = []
#     result = {
#         'event_name': "Unknown Event",
#         'event_date': "Date not found",
#         'event_time': "Time not found",
#         'event_location': "Location not found",
#         'attendees': []
#     }

#     try:
#         # print("Navigating to Luma dashboard")
#         # driver.get("https://lu.ma/")
#         # WebDriverWait(driver, 15).until(
#         #     EC.presence_of_element_located((By.TAG_NAME, "body")))
#         # time.sleep(2)

#         # Select event type tab
#         tab_selector = "button:nth-child(1)" if event_type.lower() == "upcoming" else "button:nth-child(2)"
#         print(f"Selecting {event_type} events tab")
#         WebDriverWait(driver, 15).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, tab_selector))).click()
#         time.sleep(3)

#         # Improved event finding with scrolling
#         print(f"Searching for event ID: {event_id}")
#         event_found = False
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         scroll_attempts = 0
#         max_scroll_attempts = 5
        
#         while not event_found and scroll_attempts < max_scroll_attempts:
#             try:
#                 event_card = WebDriverWait(driver, 5).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, f"a.event-link[href='/{event_id}']")))
                
#                 # Scroll element into view and click
#                 ActionChains(driver).move_to_element(event_card).perform()
#                 time.sleep(0.5)
#                 event_card.click()
#                 print("Event page opened")
#                 event_found = True
#                 break
                
#             except (NoSuchElementException, TimeoutException):
#                 print("Event not in view - scrolling...")
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(2)
                
#                 new_height = driver.execute_script("return document.body.scrollHeight")
#                 if new_height == last_height:
#                     scroll_attempts += 1
#                 last_height = new_height

#         if not event_found:
#             raise NoSuchElementException(f"Event {event_id} not found after {max_scroll_attempts} scroll attempts")

#         time.sleep(3)

#         # Extract event details (using original working selectors)
#         print("Extracting event details...")
#         try:
#             # Try multiple selectors for event name
#             name_selectors = [
#                 ("xpath", "/html/body/div[28]/div/div[2]/div/div/div/div[7]/div/div[2]/div/div[1]/div/h1"),
#                 ("css", "h1.jsx-1526065414.title.text-primary.mb-0.long"),
#                 ("css", "h1.title")
#             ]
#             for selector_type, selector in name_selectors:
#                 try:
#                     if selector_type == "xpath":
#                         result['event_name'] = driver.find_element(By.XPATH, selector).text
#                     else:
#                         result['event_name'] = driver.find_element(By.CSS_SELECTOR, selector).text
#                     break
#                 except:
#                     continue
#         except Exception as e:
#             print(f"Couldn't extract event name: {str(e)}")

#         try:
#             # Original working date extraction
#             date_el = driver.find_element(
#                 By.CSS_SELECTOR, "div.jsx-2370077516.icon-container.flex-center-center.rounded.overflow-hidden.flex-shrink-0")
#             month = date_el.find_element(By.CSS_SELECTOR, ".jsx-2109047166.month").text
#             day = date_el.find_element(By.CSS_SELECTOR, ".jsx-2109047166.day").text
#             result['event_date'] = f"{month} {day}"
#         except Exception as e:
#             print(f"Couldn't extract event date: {str(e)}")

#         try:
#             # Original working time extraction
#             result['event_time'] = driver.find_element(
#                 By.CSS_SELECTOR, "div.time-container").text
#         except Exception as e:
#             print(f"Couldn't extract event time: {str(e)}")

#         try:
#             # Original working location extraction
#             result['event_location'] = driver.find_element(
#                 By.CSS_SELECTOR, "div.location-info").text
#         except Exception as e:
#             print(f"Couldn't extract event location: {str(e)}")

#         # Open attendees modal (using original working approach)
#         print("Opening attendees section...")
#         attendee_button = None
#         for selector in [
#             "button div.guests",
#             "button[data-testid='attendees-button']",
#             "button:has(div:contains('Attendees'))"
#         ]:
#             try:
#                 attendee_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
#                 attendee_button.click()
#                 time.sleep(2)
#                 break
#             except:
#                 continue

#         if not attendee_button:
#             raise NoSuchElementException("Could not find attendee button")

#         # Find and scroll attendees modal (original working approach)
#         print("Collecting attendees...")
#         modal = WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.lux-overlay.modal")))
        
#         scroll_container = None
#         container_selectors = [
#             (By.CSS_SELECTOR, "body > div.lux-overlay.modal > div > div > div.jsx-531347415 > div.jsx-531347415.flex-column.outer.overflow-auto"),
#             (By.XPATH, "/html/body/div[62]/div/div/div[2]/div[2]"),
#             (By.CSS_SELECTOR, "div[class*='overflow-auto']")
#         ]
        
#         for by, selector in container_selectors:
#             try:
#                 scroll_container = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((by, selector)))
#                 break
#             except:
#                 continue
                
#         if not scroll_container:
#             scroll_container = modal

#         # Original working scrolling logic
#         print("Starting optimized scrolling...")
#         all_usernames = set()
#         last_count = 0
#         same_count_attempts = 0
#         max_attempts = 200  
        
#         while same_count_attempts < max_attempts:
#             current_links = scroll_container.find_elements(By.CSS_SELECTOR, "a[href^='/user/']")
#             current_count = len(current_links)
            
#             new_usernames = 0
#             for link in current_links:
#                 try:
#                     href = link.get_attribute("href")
#                     if href and "/user/" in href:
#                         username = href.split("/user/")[-1].split('?')[0].split('/')[0]
#                         if username and username not in all_usernames:
#                             all_usernames.add(username)
#                             new_usernames += 1
#                 except:
#                     continue
            
#             print(f"Total attendees: {len(all_usernames)} | New: {new_usernames} | Attempt: {same_count_attempts+1}/{max_attempts}")

#             if current_count < 8:
#                 same_count_attempts = 200 
            
#             container_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
#             current_pos = driver.execute_script("return arguments[0].scrollTop", scroll_container)
            
#             scroll_increment = 0.10 + (random.random() * 0.1)
#             scroll_amount = int(container_height * scroll_increment)
#             new_pos = current_pos + scroll_amount
            
#             if new_pos >= container_height:
#                 new_pos = container_height - 100 
#                 same_count_attempts += 1
            
#             driver.execute_script(f"arguments[0].scrollTop = {new_pos}", scroll_container)
#             time.sleep(1)
            
#             if new_pos >= container_height - 100 and new_usernames == 0:
#                 time.sleep(5)
#                 final_check = scroll_container.find_elements(By.CSS_SELECTOR, "a[href^='/user/']")
#                 final_usernames = set()
#                 for link in final_check:
#                     try:
#                         href = link.get_attribute("href")
#                         if href and "/user/" in href:
#                             username = href.split("/user/")[-1].split('?')[0].split('/')[0]
#                             if username and username not in all_usernames:
#                                 final_usernames.add(username)
#                     except:
#                         continue
                
#                 if len(final_usernames) == 0:
#                     break
#                 else:
#                     all_usernames.update(final_usernames)
#                     same_count_attempts = 0

#         usernames = list(all_usernames)
#         print(f"Total unique attendees found: {len(usernames)}")

#         # Original working profile scraping logic
#         print("Scraping attendee profiles...")
#         for i, username in enumerate(usernames):
#             try:
#                 print(f"Processing {i+1}/{len(usernames)}: {username}")
#                 driver.get(f"https://lu.ma/user/{username}")
#                 time.sleep(1 + (random.random() * 2))

#                 script = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.XPATH, "//script[@id='__NEXT_DATA__']")))
#                 data = json.loads(script.get_attribute("textContent"))
                
#                 user = data.get('props', {}).get('pageProps', {}).get('initialData', {}).get('user', {})
#                 if not user:
#                     continue
                
#                 profile = [
#                     username,
#                     user.get('name', 'N/A'),
#                     user.get('username', 'N/A'),
#                     user.get('bio_short', 'N/A'),
#                     f"{user.get('geo_city', '')}, {user.get('geo_country', '')}".strip(", "),
#                     user.get('website', 'N/A'),
#                     user.get('avatar_url', 'N/A'),
#                     user.get('event_hosted_count', 'N/A'),
#                     user.get('event_attended_count', 'N/A'),
#                     user.get('event_together_count', 'N/A'),
#                     user.get('twitter_handle', 'N/A'),
#                     user.get('instagram_handle', 'N/A'),
#                     user.get('linkedin_handle', 'N/A'),
#                     'N/A',  # telegram
#                     user.get('youtube_handle', 'N/A'),
#                     user.get('tiktok_handle', 'N/A'),
#                     'N/A',  # facebook
#                     'N/A'   # github
#                 ]
                
#                 attendees.append(profile)
                
#             except Exception as e:
#                 print(f"Error scraping {username}: {str(e)[:100]}...")
#                 continue

#         result['attendees'] = attendees
#         print(f"Successfully scraped {len(attendees)} profiles")
#         return result

#     except TimeoutException as e:
#         print(f"Timeout error: {str(e)}")
#         return result
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return result





























from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import random

def scrape_attendees(driver, event_id, event_type="past"):
    """
    Scrape attendees from Luma event with reliable event finding and proven scraping logic
    Parameters:
        driver: Selenium WebDriver instance (must be logged in)
        event_id: ID of the event to scrape
        event_type: "past" or "upcoming" (default: "upcoming")
    Returns:
        dict: Contains event details and attendees list
    """
    if not driver:
        print("Driver not initialized.")
        return {
            'event_name': "Unknown Event",
            'event_date': "Date not found",
            'event_time': "Time not found",
            'event_location': "Location not found",
            'attendees': []
        }

    attendees = []
    result = {
        'event_name': "Unknown Event",
        'event_date': "Date not found",
        'event_time': "Time not found",
        'event_location': "Location not found",
        'attendees': []
    }

    try:
        # Select event type tab
        tab_selector = "button:nth-child(1)" if event_type.lower() == "upcoming" else "button:nth-child(2)"
        print(f"Selecting {event_type} events tab")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, tab_selector))).click()
        time.sleep(3)

        # Improved event finding with scrolling
        print(f"Searching for event ID: {event_id}")
        event_found = False
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 5
        
        while not event_found and scroll_attempts < max_scroll_attempts:
            try:
                event_card = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"a.event-link[href='/{event_id}']")))
                
                # Scroll element into view and click
                ActionChains(driver).move_to_element(event_card).perform()
                time.sleep(0.5)
                event_card.click()
                print("Event page opened")
                event_found = True
                break
                
            except (NoSuchElementException, TimeoutException):
                print("Event not in view - scrolling...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                last_height = new_height

        if not event_found:
            raise NoSuchElementException(f"Event {event_id} not found after {max_scroll_attempts} scroll attempts")

        time.sleep(3)

        # Extract event details (using original working selectors)
        print("Extracting event details...")
        try:
            # Try multiple selectors for event name
            name_selectors = [
                ("xpath", "/html/body/div[28]/div/div[2]/div/div/div/div[7]/div/div[2]/div/div[1]/div/h1"),
                ("css", "h1.jsx-1526065414.title.text-primary.mb-0.long"),
                ("css", "h1.title")
            ]
            for selector_type, selector in name_selectors:
                try:
                    if selector_type == "xpath":
                        result['event_name'] = driver.find_element(By.XPATH, selector).text
                    else:
                        result['event_name'] = driver.find_element(By.CSS_SELECTOR, selector).text
                    break
                except:
                    continue
        except Exception as e:
            print(f"Couldn't extract event name: {str(e)}")

        try:
            # Original working date extraction
            date_el = driver.find_element(
                By.CSS_SELECTOR, "div.jsx-2370077516.icon-container.flex-center-center.rounded.overflow-hidden.flex-shrink-0")
            month = date_el.find_element(By.CSS_SELECTOR, ".jsx-2109047166.month").text
            day = date_el.find_element(By.CSS_SELECTOR, ".jsx-2109047166.day").text
            result['event_date'] = f"{month} {day}"
        except Exception as e:
            print(f"Couldn't extract event date: {str(e)}")

        try:
            # Original working time extraction
            result['event_time'] = driver.find_element(
                By.CSS_SELECTOR, "div.time-container").text
        except Exception as e:
            print(f"Couldn't extract event time: {str(e)}")

        try:
            # Original working location extraction
            result['event_location'] = driver.find_element(
                By.CSS_SELECTOR, "div.location-info").text
        except Exception as e:
            print(f"Couldn't extract event location: {str(e)}")

        # Open attendees modal (using original working approach)
        print("Opening attendees section...")
        attendee_button = None
        for selector in [
            "button div.guests",
            "button[data-testid='attendees-button']",
            "button:has(div:contains('Attendees'))"
        ]:
            try:
                attendee_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                attendee_button.click()
                time.sleep(2)
                break
            except:
                continue

        if not attendee_button:
            raise NoSuchElementException("Could not find attendee button")

        # Improved modal handling and scrolling
        print("Collecting attendees...")
        modal = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.lux-overlay.modal")))
        
        # Find the scrollable container more reliably
        scroll_container = None
        container_selectors = [
            "div[class*='overflow-auto']",  # Most likely selector
            "div.lux-overlay-content",     # Fallback 1
            "div.modal-content",           # Fallback 2
            "div[role='dialog']"           # Fallback 3
        ]
        
        for selector in container_selectors:
            try:
                scroll_container = WebDriverWait(modal, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except:
                continue
                
        if not scroll_container:
            scroll_container = modal

        # Improved scrolling logic with better detection
        print("Starting optimized scrolling...")
        all_usernames = set()
        last_count = 0
        same_count_attempts = 0
        max_attempts = 15  # Reduced from 200 to prevent excessive scrolling
        
        while same_count_attempts < max_attempts:
            # Find all user links in the container
            current_links = scroll_container.find_elements(By.CSS_SELECTOR, "a[href^='/user/']")
            current_count = len(current_links)
            
            # Extract new usernames
            new_usernames = 0
            for link in current_links:
                try:
                    href = link.get_attribute("href")
                    if href and "/user/" in href:
                        username = href.split("/user/")[-1].split('?')[0].split('/')[0]
                        if username and username not in all_usernames:
                            all_usernames.add(username)
                            new_usernames += 1
                except:
                    continue
            
            print(f"Total attendees: {len(all_usernames)} | New: {new_usernames} | Attempt: {same_count_attempts+1}/{max_attempts}")

            # If no new usernames found in this iteration, increment counter
            if new_usernames == 0:
                same_count_attempts += 1
            else:
                same_count_attempts = 0  # Reset counter if we found new users
            
            # Scroll down in the container
            container_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            current_pos = driver.execute_script("return arguments[0].scrollTop", scroll_container)
            
            # Calculate scroll amount (randomized to appear more natural)
            scroll_amount = min(
                500 + int(random.random() * 300),  # Scroll between 500-800px
                container_height - current_pos - 100  # Don't overshoot
            )
            
            driver.execute_script(f"arguments[0].scrollTop = {current_pos + scroll_amount}", scroll_container)
            time.sleep(0.5 + random.random())  # Random delay between 0.5-1.5 seconds
            
            # Check if we've reached the bottom
            new_pos = driver.execute_script("return arguments[0].scrollTop", scroll_container)
            if new_pos + scroll_container.size['height'] >= container_height:
                same_count_attempts += 1  # We're at the bottom

        usernames = list(all_usernames)
        print(f"Total unique attendees found: {len(usernames)}")

        # Original working profile scraping logic
        print("Scraping attendee profiles...")
        for i, username in enumerate(usernames):
            try:
                print(f"Processing {i+1}/{len(usernames)}: {username}")
                driver.get(f"https://lu.ma/user/{username}")
                time.sleep(1 + (random.random() * 2))

                script = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//script[@id='__NEXT_DATA__']")))
                data = json.loads(script.get_attribute("textContent"))
                
                user = data.get('props', {}).get('pageProps', {}).get('initialData', {}).get('user', {})
                if not user:
                    continue
                
                profile = [
                    username,
                    user.get('name', 'N/A'),
                    user.get('username', 'N/A'),
                    user.get('bio_short', 'N/A'),
                    f"{user.get('geo_city', '')}, {user.get('geo_country', '')}".strip(", "),
                    user.get('website', 'N/A'),
                    user.get('avatar_url', 'N/A'),
                    user.get('event_hosted_count', 'N/A'),
                    user.get('event_attended_count', 'N/A'),
                    user.get('event_together_count', 'N/A'),
                    user.get('twitter_handle', 'N/A'),
                    user.get('instagram_handle', 'N/A'),
                    user.get('linkedin_handle', 'N/A'),
                    'N/A',  # telegram
                    user.get('youtube_handle', 'N/A'),
                    user.get('tiktok_handle', 'N/A'),
                    'N/A',  # facebook
                    'N/A'   # github
                ]
                
                attendees.append(profile)
                
            except Exception as e:
                print(f"Error scraping {username}: {str(e)[:100]}...")
                continue

        result['attendees'] = attendees
        print(f"Successfully scraped {len(attendees)} profiles")
        return result

    except TimeoutException as e:
        print(f"Timeout error: {str(e)}")
        return result
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return result







