
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time
import random

def scrape_attendees(driver, event_id, event_type):
    """
    Scrape attendees from Luma event with event details extraction
    Parameters:
        driver: Selenium WebDriver instance
        event_id: ID of the event to scrape
        event_type: "past" or "upcoming" (default: "upcoming")
    Returns:
        tuple: (event_name, event_date, attendees_list)
    """
    if not driver:
        print("Login failed.")
        return None, None, []

    attendees = []
    usernames = []
    event_name = "Unknown Event"
    event_date = "Date not found"
    event_time = "Time not found"
    event_location = "Location not found"

    try:
        print("Navigating to Luma dashboard")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)

        # Determine which tab to click based on event type
        if event_type.lower() == "upcoming":
            print("Clicking on Upcoming events tab")
            event_button_selector = "button:nth-child(1)"
        else:
            print("Clicking on Past events tab.")
            event_button_selector = "button:nth-child(2)"

        event_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, event_button_selector)))
        event_button.click()
        time.sleep(3)

        print(f"Looking for event with ID: {event_id}")
        event_card = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"a.event-link[href='/{event_id}']")))
        event_card.click()
        print("Event page opened")
        time.sleep(3)

        # Extract event name
        try:
            selectors = [
                ("xpath", "/html/body/div[28]/div/div[2]/div/div/div/div[7]/div/div[2]/div/div[1]/div/h1"),
                ("css", "h1.jsx-1526065414.title.text-primary.mb-0.long"),
                ("css", "div.jsx-1526065414.title-wrapper h1"),
                ("css", "h1.title")
            ]
            
            for selector_type, selector in selectors:
                try:
                    if selector_type == "xpath":
                        event_name_element = driver.find_element(By.XPATH, selector)
                    else:
                        event_name_element = driver.find_element(By.CSS_SELECTOR, selector)
                    event_name = event_name_element.text
                    print(f"Extracted event name: {event_name}")
                    break
                except NoSuchElementException:
                    continue
        except Exception as e:
            print(f"Could not extract event name: {str(e)}")

        # Extract event date and time
        try:
            # Date element
            date_selectors = [
                ("xpath", "/html/body/div[28]/div/div[2]/div/div/div/div[7]/div/div[2]/div/div[3]/div/div[1]/div[1]"),
                ("css", "div.jsx-2370077516.icon-container.flex-center-center.rounded.overflow-hidden.flex-shrink-0")
            ]
            
            for selector_type, selector in date_selectors:
                try:
                    if selector_type == "xpath":
                        date_element = driver.find_element(By.XPATH, selector)
                    else:
                        date_element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    month = date_element.find_element(By.CSS_SELECTOR, ".jsx-2109047166.month").text
                    day = date_element.find_element(By.CSS_SELECTOR, ".jsx-2109047166.day").text
                    event_date = f"{month} {day}"
                    print(f"Extracted event date: {event_date}")
                    break
                except NoSuchElementException:
                    continue

            time_selectors = [
                ("css", "div.time-container"), 
                ("xpath", "//div[contains(@class, 'time-info')]") 
            ]
            
            for selector_type, selector in time_selectors:
                try:
                    if selector_type == "xpath":
                        time_element = driver.find_element(By.XPATH, selector)
                    else:
                        time_element = driver.find_element(By.CSS_SELECTOR, selector)
                    event_time = time_element.text
                    print(f"Extracted event time: {event_time}")
                    break
                except NoSuchElementException:
                    continue

            location_selectors = [
                ("css", "div.location-info"),  
                ("xpath", "//div[contains(@class, 'venue')]")  
            ]
            
            for selector_type, selector in location_selectors:
                try:
                    if selector_type == "xpath":
                        location_element = driver.find_element(By.XPATH, selector)
                    else:
                        location_element = driver.find_element(By.CSS_SELECTOR, selector)
                    event_location = location_element.text
                    print(f"Extracted event location: {event_location}")
                    break
                except NoSuchElementException:
                    continue

        except Exception as e:
            print(f"Could not extract event details: {str(e)}")

        print("Attempting to open attendee section.")
        attendee_selectors = [
            "button div.guests",
            "button[data-testid='attendees-button']",
            "button:has(div:contains('Attendees'))"
        ]
        
        attendee_button = None
        for selector in attendee_selectors:
            try:
                attendee_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except (NoSuchElementException, TimeoutException):
                continue
                
        if not attendee_button:
            raise NoSuchElementException("Could not find attendee button with any selector")
            
        attendee_button.click()
        time.sleep(2)

        print("Collecting attendee usernames from modal...")
        modal = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.lux-overlay.modal"))
        )
        
        # Find the scrollable container - trying multiple selectors

        scroll_container = None
        container_selectors = [
            (By.CSS_SELECTOR, "body > div.lux-overlay.modal > div > div > div.jsx-531347415 > div.jsx-531347415.flex-column.outer.overflow-auto"),
            (By.XPATH, "/html/body/div[62]/div/div/div[2]/div[2]"),
            (By.CSS_SELECTOR, "div[class*='overflow-auto']")
        ]
        
        for by, selector in container_selectors:
            try:
                scroll_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((by, selector)))
                print(f"Found scroll container using {selector}")
                break
            except Exception as e:
                print(f"Could not find container with {selector}: {str(e)}")
                continue
                
        if not scroll_container:
            print("Using modal as fallback scroll container")
            scroll_container = modal

        print("Starting optimized scrolling to load all attendees...")
        all_usernames = set()
        last_count = 0
        same_count_attempts = 0
        max_attempts = 200  
        scroll_increment = 0.1  
        
       

        while same_count_attempts < max_attempts:

            # Get all current attendee links

            current_links = scroll_container.find_elements(By.CSS_SELECTOR, "a[href^='/user/']")
            current_count = len(current_links)
            
            # Collect new usernames

            new_usernames = 0
            for link in current_links:
                try:
                    href = link.get_attribute("href")
                    if href and "/user/" in href:
                        username = href.split("/user/")[-1].split('?')[0].split('/')[0]
                        if username and username not in all_usernames:
                            all_usernames.add(username)
                            new_usernames += 1
                except Exception as e:
                    print(f"Error extracting username: {str(e)}")
                    continue
            
            print(f"Total attendees: {len(all_usernames)} | New this batch: {new_usernames} | Attempt: {same_count_attempts+1}/{max_attempts}")

            if(current_count<8):
                same_count_attempts=200 
            
            # Randomize scroll behavior to prevent detection

            container_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            current_pos = driver.execute_script("return arguments[0].scrollTop", scroll_container)
            
            # Dynamic scroll increment (10-25% of container height)

            scroll_increment = 0.10 + (random.random() * 0.1)
            scroll_amount = int(container_height * scroll_increment)
            new_pos = current_pos + scroll_amount
            
            # Don't scroll past the bottom

            if new_pos >= container_height:
                new_pos = container_height - 100 
                same_count_attempts += 1
            
            # Perform the scroll

            driver.execute_script(f"arguments[0].scrollTop = {new_pos}", scroll_container)
            
        
            wait_time =1
            time.sleep(wait_time)
            
            # Check if we're still loading new attendees

            new_links = scroll_container.find_elements(By.CSS_SELECTOR, "a[href^='/user/']")
            if len(new_links) == current_count:
                same_count_attempts += 1

                # Increase scroll increment if  stuck

                scroll_increment = min(scroll_increment * 1.2, 0.5)  # Cap at 50%
            else:
                same_count_attempts = 0
                scroll_increment = 0.15  

                
            # Early exit if we've scrolled to bottom and no new attendees
          
            if new_pos >= container_height - 100 and new_usernames == 0:

                # Wait longer and check again before exiting

                print("Possible bottom reached - waiting 5 seconds to confirm...")
                time.sleep(5)  
                
                # Check one more time for new usernames

                final_check_links = scroll_container.find_elements(By.CSS_SELECTOR, "a[href^='/user/']")
                final_usernames = set()
                for link in final_check_links:
                    try:
                        href = link.get_attribute("href")
                        if href and "/user/" in href:
                            username = href.split("/user/")[-1].split('?')[0].split('/')[0]
                            if username and username not in all_usernames:
                                final_usernames.add(username)
                    except:
                        continue
                
                if len(final_usernames) == 0:
                    print("Confirmed no new attendees after waiting - ending scroll")
                    break
                else:
                    print(f"Found {len(final_usernames)} new attendees after wait - continuing")
                    all_usernames.update(final_usernames)
                    same_count_attempts = 0  # Reset counter since we found new ones
                        

        usernames = list(all_usernames)
        print(f"Total unique attendees found: {len(usernames)}")

        # Now visit each profile to get detailed info
        for i, username in enumerate(usernames):
            try:
                print(f"Processing attendee {i+1}/{len(usernames)}: {username}")
                profile_url = f"https://lu.ma/user/{username}"
                driver.get(profile_url)
                
                # Random wait time between 1-3 seconds
                time.sleep(1 + (random.random() * 2))

                # Wait for the __NEXT_DATA__ script

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//script[@id='__NEXT_DATA__']")))

                # Extract JSON data
                
                script_element = driver.find_element(By.XPATH, "//script[@id='__NEXT_DATA__']")
                next_data = json.loads(script_element.get_attribute("textContent"))


                user_data = {}
                try:
                    user_data = next_data['props']['pageProps']['initialData']['user']
                except KeyError:
                    try:
                        user_data = next_data['props']['initialUserData']['user']
                    except KeyError:
                        print(f"Couldn't find user data for {username}")
                        continue

                if not user_data:
                    continue

                # Process social links

                social_links = {
                    'twitter': user_data.get('twitter_handle'),
                    'instagram': user_data.get('instagram_handle'),
                    'linkedin': user_data.get('linkedin_handle'),
                    'youtube': user_data.get('youtube_handle'),
                    'tiktok': user_data.get('tiktok_handle')
                }
                social_links = {k: v for k, v in social_links.items() if v}

                # Get event stats
                event_stats = next_data.get('props', {}).get('pageProps', {}).get('initialData', {})
                events_hosted = event_stats.get('event_hosted_count', 'N/A')
                events_attended = event_stats.get('event_attended_count', 'N/A')
                events_together = event_stats.get('event_together_count', 'N/A')

                # Create profile data
                
                profile_data = [
                    username,
                    user_data.get('name', 'N/A'),
                    user_data.get('username', 'N/A'),
                    user_data.get('bio_short', 'N/A'),
                    f"{user_data.get('geo_city', '')}, {user_data.get('geo_country', '')}".strip(", "),
                    user_data.get('website', 'N/A'),
                    user_data.get('avatar_url', 'N/A'),
                    events_hosted,
                    events_attended,
                    events_together,
                    social_links.get('twitter', 'N/A'),
                    social_links.get('instagram', 'N/A'),
                    social_links.get('linkedin', 'N/A'),
                    'N/A',  # telegram
                    social_links.get('youtube', 'N/A'),
                    social_links.get('tiktok', 'N/A'),
                    'N/A',  # facebook
                    'N/A'   # github
                ]

                attendees.append(profile_data)
                print(f"Scraped: {user_data.get('name', username)}")

            except Exception as e:
                print(f"Failed to scrape profile for {username}: {str(e)[:100]}...")
                continue

        print(f"\nSuccessfully scraped detailed info for {len(attendees)} attendees")
        return {
            'event_name': event_name,
            'event_date': event_date,
            'event_time': event_time,
            'event_location': event_location,
            'attendees': attendees
        }

    except TimeoutException as e:
        print(f"Timeout while scraping: {str(e)}")
        return {
            'event_name': event_name,
            'event_date': event_date,
            'event_time': event_time,
            'event_location': event_location,
            'attendees': []
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'event_name': event_name,
            'event_date': event_date,
            'event_time': event_time,
            'event_location': event_location,
            'attendees': []
        }