"""
LinkedIn Feed Scraper
Scrolls through LinkedIn feed and extracts post descriptions.

Requirements:
pip install selenium webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

class LinkedInScraper:
    def __init__(self, use_profile=True):
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use a separate Chrome profile for Selenium
        if use_profile:
            import os
            # Create a selenium-specific profile directory
            selenium_profile = os.path.join(os.getcwd(), 'selenium_profile')
            options.add_argument(f'--user-data-dir={selenium_profile}')
            
            print("\n" + "="*60)
            print("Using a separate Chrome profile for automation.")
            print("You'll need to log into LinkedIn in this window.")
            print("="*60 + "\n")
        
        # Initialize driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.posts = []
        
    def login_prompt(self):
        """Navigate to LinkedIn and wait for it to load"""
        print("\nOpening LinkedIn...")
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            print("\n" + "="*50)
            print("Waiting for LinkedIn to load...")
            print("If you're not logged in, please log in now.")
            print("Press Enter once you can see your feed...")
            print("="*50 + "\n")
            input()
        except Exception as e:
            print(f"Error during navigation: {e}")
            raise
        
    def scroll_and_extract(self, num_scrolls=10, scroll_pause=2):
        """Scroll through feed and extract post descriptions"""
        print(f"Starting to scroll and extract posts...")
        print(f"Will perform {num_scrolls} scrolls\n")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        seen_posts = set()
        
        for scroll_num in range(num_scrolls):
            # Get all posts currently visible
            try:
                # Expand all "see more" buttons before extracting
                try:
                    see_more_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "button.feed-shared-inline-show-more-text__see-more-less-toggle, "
                        "button[aria-label*='see more'], "
                        "button.see-more"
                    )
                    for button in see_more_buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                self.driver.execute_script("arguments[0].click();", button)
                                time.sleep(0.2)
                        except:
                            continue
                except:
                    pass
                
                # Get all posts - including reposts and shared posts
                post_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "div.feed-shared-update-v2, "
                    "div[data-urn*='activity'], "
                    "div.feed-shared-update-v2__content"
                )
                
                for post in post_elements:
                    try:
                        # Get unique identifier for the post
                        post_id = post.get_attribute('data-urn')
                        if not post_id:
                            post_id = post.get_attribute('data-id')
                        if not post_id:
                            # Generate a fallback ID
                            post_id = f"post_{len(seen_posts)}"
                        
                        if post_id and post_id not in seen_posts:
                            seen_posts.add(post_id)
                            
                            # Extract post description/text
                            description = ""
                            description_element = None
                            
                            # Try different selectors for post content
                            selectors = [
                                "div.feed-shared-update-v2__description",
                                "div.update-components-text",
                                "span.break-words",
                                "div.feed-shared-text",
                                "span.feed-shared-text__text-view",
                                "div.feed-shared-inline-show-more-text",
                                "div.feed-shared-text__text-view"
                            ]
                            
                            for selector in selectors:
                                try:
                                    description_element = post.find_element(By.CSS_SELECTOR, selector)
                                    description = description_element.text.strip()
                                    if description:
                                        # Remove "...see more" text if present
                                        description = description.replace("…see more", "").replace("...see more", "").strip()
                                        break
                                except:
                                    continue
                            
                            # Extract emails using regex from description
                            import re
                            emails = []
                            if description:
                                # Match standard email format
                                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                                emails = re.findall(email_pattern, description)
                            
                            # Also check for mailto links
                            try:
                                mailto_links = post.find_elements(By.CSS_SELECTOR, "a[href^='mailto:']")
                                for link in mailto_links:
                                    href = link.get_attribute('href')
                                    if href:
                                        # Extract email from mailto:email@example.com
                                        email = href.replace('mailto:', '').split('?')[0]
                                        if email and email not in emails:
                                            emails.append(email)
                            except:
                                pass
                            
                            # Get author name with multiple selectors
                            author = "Unknown"
                            author_selectors = [
                                "span.update-components-actor__name",
                                "span[dir='ltr'] > span[aria-hidden='true']",
                                "a.update-components-actor__meta-link span",
                                "div.update-components-actor__name",
                                "span.feed-shared-actor__name",
                                ".update-components-actor__title span",
                                "span.update-components-actor__title"
                            ]
                            
                            for selector in author_selectors:
                                try:
                                    author_element = post.find_element(By.CSS_SELECTOR, selector)
                                    author = author_element.text.strip()
                                    if author and author != "Unknown" and len(author) > 2:
                                        break
                                except:
                                    continue
                            
                            # Only save if we have description or emails
                            if description or emails:
                                post_data = {
                                    'author': author,
                                    'description': description,
                                    'emails': list(set(emails))  # Remove duplicates
                                }
                                self.posts.append(post_data)
                                
                                # Print extraction info
                                info = f"Post #{len(self.posts)} from {author}"
                                if emails:
                                    info += f" | Emails: {', '.join(emails)}"
                                print(info)
                    
                    except Exception as e:
                        continue
                
            except Exception as e:
                print(f"Error extracting posts: {e}")
            
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            print(f"Scroll {scroll_num + 1}/{num_scrolls} complete. Total posts: {len(self.posts)}")
            
            # Break if we've reached the end
            if new_height == last_height:
                print("Reached end of feed")
                break
                
            last_height = new_height
        
        print(f"\n{'='*50}")
        print(f"Extraction complete! Total posts extracted: {len(self.posts)}")
        print(f"Total emails found: {sum(len(p['emails']) for p in self.posts)}")
        print(f"{'='*50}\n")
    
    def save_to_file(self, filename='linkedin_posts.json'):
        """Save extracted posts to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, indent=2, ensure_ascii=False)
        print(f"Posts saved to {filename}")
    
    def print_posts(self, limit=5):
        """Print first few posts to console"""
        print(f"\nShowing first {min(limit, len(self.posts))} posts:\n")
        for i, post in enumerate(self.posts[:limit], 1):
            print(f"--- Post {i} ---")
            print(f"Author: {post['author']}")
            print(f"Description: {post['description'][:300]}..." if len(post['description']) > 300 else f"Description: {post['description']}")
            if post['emails']:
                print(f"Emails found: {', '.join(post['emails'])}")
            print()
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("Browser closed")


def main():
    scraper = LinkedInScraper()
    
    try:
        # Step 1: Open LinkedIn and wait for manual login
        scraper.login_prompt()
        
        # Step 2: Scroll and extract posts
        # Adjust num_scrolls and scroll_pause as needed
        scraper.scroll_and_extract(num_scrolls=20, scroll_pause=2)
        
        # Step 3: Display sample posts
        scraper.print_posts(limit=5)
        
        # Step 4: Save to file
        scraper.save_to_file('linkedin_posts.json')
        
        # Keep browser open to review
        print("\nExtraction complete!")
        input("Press Enter to close the browser...")
        
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            scraper.close()
        except:
            print("Browser was already closed")


if __name__ == "__main__":
    main()