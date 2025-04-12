
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time

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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)

        # Determine which tab to click based on event type

        if event_type.lower() == "upcoming":
            print("Clicking on Upcoming events tab")
            event_button_selector = "button:nth-child(1)"
        else:
            print("Clicking on Past events tab.")
            event_button_selector = "button:nth-child(2)"

        event_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, event_button_selector)))
        event_button.click()
        time.sleep(3)

        print(f"Looking for event with ID: {event_id}")
        event_card = WebDriverWait(driver, 10).until(
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
                attendee_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                break
            except (NoSuchElementException, TimeoutException):
                continue
                
        if not attendee_button:
            raise NoSuchElementException("Could not find attendee button with any selector")
            
        attendee_button.click()
        time.sleep(2)

        print("Collecting attendee usernames from modal...")
        modal_selectors = [
            "div.lux-overlay.modal",
            "div[role='dialog']",
            "div.attendee-modal"
        ]
        
        modal = None
        for selector in modal_selectors:
            try:
                modal = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except (NoSuchElementException, TimeoutException):
                continue
                
        if not modal:
            raise NoSuchElementException("Could not find attendee modal with any selector")
            
        time.sleep(1)

        # Scroll to load all attendees

        print("Scrolling to load all attendees...")
        last_height = driver.execute_script("return arguments[0].scrollHeight", modal)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(1)
            new_height = driver.execute_script("return arguments[0].scrollHeight", modal)
            if new_height == last_height:
                break
            last_height = new_height

        # Get all profile links to extract usernames

        profile_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href^='/user/']")))

        # Extract unique usernames
        usernames = list(set(
            link.get_attribute("href").split("/user/")[-1]
            for link in profile_links
            if link.get_attribute("href") and "/user/" in link.get_attribute("href")
        ))

        print(f"Found {len(usernames)} unique attendees to scrape")

        # Now visit each profile to get detailed info

        for username in usernames:
            try:
                profile_url = f"https://lu.ma/user/{username}"
                driver.get(profile_url)
                time.sleep(3)

                # Wait for the __NEXT_DATA__ script
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//script[@id='__NEXT_DATA__']")))

                # Extract JSON data
                script_element = driver.find_element(By.XPATH, "//script[@id='__NEXT_DATA__']")
                next_data = json.loads(script_element.get_attribute("textContent"))

                # Extract user data
                try:
                    user_data = next_data['props']['pageProps']['initialData']['user']
                except KeyError:
                    try:
                        user_data = next_data['props']['initialUserData']['user']
                    except KeyError:
                        print(f"Couldn't find user data for {username}")
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
                event_stats = next_data['props']['pageProps']['initialData']
                events_hosted = event_stats.get('event_hosted_count', 'N/A')
                events_attended = event_stats.get('event_attended_count', 'N/A')
                events_together = event_stats.get('event_together_count', 'N/A')

                # Create profile data

                profile_data = {
                    'username': username,
                    'name': user_data.get('name', 'N/A'),
                    'username_display': user_data.get('username', 'N/A'),
                    'bio': user_data.get('bio_short', 'N/A'),
                    'location': f"{user_data.get('geo_city', '')}, {user_data.get('geo_country', '')}".strip(", "),
                    'website': user_data.get('website', 'N/A'),
                    'profile_image': user_data.get('avatar_url', 'N/A'),
                    'events_hosted': events_hosted,
                    'events_attended': events_attended,
                    'events_together': events_together,
                    'social_links': social_links
                }

                # Add to attendees list
                
                attendees.append([
                    profile_data['username'],
                    profile_data['name'],
                    profile_data['username_display'],
                    profile_data['bio'],
                    profile_data['location'],
                    profile_data['website'],
                    profile_data['profile_image'],
                    profile_data['events_hosted'],
                    profile_data['events_attended'],
                    profile_data['events_together'],
                    profile_data['social_links'].get('twitter', 'N/A'),
                    profile_data['social_links'].get('instagram', 'N/A'),
                    profile_data['social_links'].get('linkedin', 'N/A'),
                    'N/A',  # telegram
                    profile_data['social_links'].get('youtube', 'N/A'),
                    profile_data['social_links'].get('tiktok', 'N/A'),
                    'N/A',  # facebook
                    'N/A'   # github
                ])

                print(f"\nScraped: {profile_data['name']} (@{profile_data['username_display']})")
                print(f"   - Bio: {profile_data['bio']}")
                print(f"   - Location: {profile_data['location']}")
                print(f"   - Website: {profile_data['website']}")
                print(f"   - Events: Hosted {profile_data['events_hosted']}, Attended {profile_data['events_attended']}")
                print(f"   - Social Links: {profile_data['social_links'] or 'None found'}")

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