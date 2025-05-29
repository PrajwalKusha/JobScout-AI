import undetected_chromedriver as uc
import chromedriver_autoinstaller 
chromedriver_autoinstaller.install() 
from bs4 import BeautifulSoup
import json
import time
import random
import asyncio
import aiohttp
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from utils.logger import job_scraper_logger
from utils.exceptions import ScrapingError, BrowserError, RateLimitError, JobScraperError
import os

class IndeedScraper:
    def __init__(self, max_retries=3, retry_delay=5, max_workers=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_workers = max_workers
        self.driver = None
        self.session = None
        self.wait = None

    def setup_driver(self):
        """Set up the Chrome driver with appropriate options."""
        try:
            job_scraper_logger.info("Setting up Chrome driver")
            options = uc.ChromeOptions()

            # Basic options that are supported by undetected_chromedriver
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-notifications")
            options.add_argument("--start-maximized")
            options.add_argument("--headless=new")  # ADD THIS LINE (ensure headless on cloud)

            # Create the driver with minimal options
            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                version_main=None,
            )

            # Set up wait after driver is created
            self.wait = WebDriverWait(self.driver, 15)  # Increased timeout to 15 seconds

            job_scraper_logger.info("Chrome driver setup successful")
        except Exception as e:
            error_msg = f"Failed to setup Chrome driver: {str(e)}"
            job_scraper_logger.error(error_msg)
            raise BrowserError(error_msg) from e

    def check_for_verification(self) -> bool:
        """
        Check if we're on a verification page.
        
        Returns:
            bool: True if on verification page, False otherwise
        """
        try:
            # Check for common verification page elements
            verification_indicators = [
                "//h1[contains(text(), 'Verify you are a human')]",
                "//h1[contains(text(), 'Verify you are not a robot')]",
                "//div[contains(@class, 'captcha')]",
                "//iframe[contains(@src, 'captcha')]",
                "//div[contains(@class, 'challenge-dialog')]"
            ]
            
            for xpath in verification_indicators:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    if element.is_displayed():
                        job_scraper_logger.warning("Detected verification page")
                        return True
                except NoSuchElementException:
                    continue
            
            return False
        except Exception as e:
            job_scraper_logger.warning(f"Error checking for verification: {str(e)}")
            return False

    def handle_verification(self) -> bool:
        """
        Handle the verification page by waiting for manual intervention.
        
        Returns:
            bool: True if verification was successful, False otherwise
        """
        try:
            job_scraper_logger.info("Waiting for manual verification...")
            print("\nPlease complete the verification on the browser window.")
            print("After completing verification, press Enter to continue...")
            input()
            
            # Wait a bit after verification
            time.sleep(random.uniform(2, 4))
            
            # Check if we're still on verification page
            if self.check_for_verification():
                job_scraper_logger.error("Still on verification page after manual intervention")
                return False
            
            # Wait for the page to load after verification
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon, div.no_results"))
                )
                return True
            except TimeoutException:
                job_scraper_logger.error("Page did not load properly after verification")
                return False
                
        except Exception as e:
            job_scraper_logger.error(f"Error during verification: {str(e)}")
            return False

    def simulate_human_behavior(self):
        """Simulate human-like behavior to avoid detection."""
        try:
            # Random scrolling with smooth behavior
            for _ in range(random.randint(2, 4)):
                scroll_amount = random.randint(100, 500)
                self.driver.execute_script(f"""
                    window.scrollTo({{
                        top: {scroll_amount},
                        behavior: 'smooth'
                    }});
                """)
                time.sleep(random.uniform(0.5, 1.5))
            
            # Random mouse movements (simulated)
            for _ in range(random.randint(3, 6)):
                x = random.randint(0, 1000)
                y = random.randint(0, 1000)
                self.driver.execute_script("""
                    var event = new MouseEvent('mousemove', {
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': arguments[0],
                        'clientY': arguments[1]
                    });
                    document.dispatchEvent(event);
                """, x, y)
                time.sleep(random.uniform(0.2, 0.5))
            
            # Random pauses
            time.sleep(random.uniform(0.3, 1.0))
            
            # Simulate random clicks on non-interactive elements
            if random.random() < 0.3:  # 30% chance to click
                self.driver.execute_script("""
                    var elements = document.getElementsByTagName('div');
                    if (elements.length > 0) {
                        var randomElement = elements[Math.floor(Math.random() * elements.length)];
                        var event = new MouseEvent('click', {
                            'view': window,
                            'bubbles': true,
                            'cancelable': true
                        });
                        randomElement.dispatchEvent(event);
                    }
                """)
        except Exception as e:
            job_scraper_logger.warning(f"Error during human behavior simulation: {str(e)}")

    def wait_for_job_cards(self, timeout=20):
        """
        Wait for job cards to appear on the page.
        
        Args:
            timeout (int): Maximum time to wait in seconds
            
        Returns:
            bool: True if job cards are found, False otherwise
        """
        try:
            # First check for verification page
            if self.check_for_verification():
                if not self.handle_verification():
                    return False
            
            # Wait for the page to be fully loaded
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for either job cards or the "no results" message
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon, div.no_results, div.jobsearch-ResultsList"))
                )
            except TimeoutException:
                job_scraper_logger.warning("Timeout waiting for job results container")
                return False
            
            # Check if we got the "no results" message
            no_results = self.driver.find_elements(By.CSS_SELECTOR, "div.no_results")
            if no_results:
                job_scraper_logger.warning("No job results found for the search criteria")
                return False
            
            # Additional check for job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
            if not job_cards:
                job_scraper_logger.warning("No job cards found in the results")
                return False
                
            return True
        except TimeoutException:
            job_scraper_logger.warning("Timeout waiting for job cards")
            return False
        except Exception as e:
            job_scraper_logger.warning(f"Error waiting for job cards: {str(e)}")
            return False

    def extract_salary(self, soup: BeautifulSoup, is_detail_page: bool = False) -> Optional[str]:
        """
        Extract salary information from a BeautifulSoup object.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the page
            is_detail_page (bool): Whether this is a detail page
            
        Returns:
            Optional[str]: Extracted salary information
        """
        selectors = [
            "div.salary-snippet-container",
            "div[data-testid='salary-snippet']",
            "div.attribute_snippet",
            "span.salaryText",
            "div.metadata-salary-container",
            "div.jobsearch-JobComponent-description div[data-testid='jobDescriptionText'] span.salaryText",
            "div.jobsearch-JobComponent-description div[data-testid='jobDescriptionText'] div.salary-snippet",
            "div.jobsearch-JobComponent-description div[data-testid='jobDescriptionText'] div[class*='salary']",
            "div.jobsearch-JobComponent-description div[data-testid='jobDescriptionText'] span[class*='salary']",
            "div.jobsearch-JobComponent-description div[data-testid='jobDescriptionText'] div[class*='compensation']",
            "div.jobsearch-JobComponent-description div[data-testid='jobDescriptionText'] span[class*='compensation']"
        ]
        
        for selector in selectors:
            salary_tag = soup.select_one(selector)
            if salary_tag:
                salary_text = salary_tag.get_text(strip=True)
                if salary_text and any(keyword in salary_text.lower() for keyword in ['salary', 'compensation', 'pay', '$', 'k', 'hour']):
                    return salary_text
        return None

    async def get_job_details_async(self, job_link: str) -> Optional[str]:
        """
        Get detailed information about a job from its detail page asynchronously.
        
        Args:
            job_link (str): URL of the job detail page
            
        Returns:
            Optional[str]: Full job description
        """
        try:
            # Use Selenium to get the page content
            self.driver.get(job_link)
            time.sleep(random.uniform(2, 3))  # Wait for JavaScript to load
            
            # Wait for the job description to be present
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div#jobDescriptionText, div.jobsearch-JobComponent-description"))
                )
            except TimeoutException:
                job_scraper_logger.warning("Timeout waiting for job description")
                return None
            
            # Get the page source and parse it
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            # Try different selectors for job description
            desc_selectors = [
                "div#jobDescriptionText",
                "div.jobsearch-JobComponent-description",
                "div[data-testid='jobDescriptionText']",
                "div.jobsearch-jobDescriptionText"
            ]
            
            for selector in desc_selectors:
                desc_div = soup.select_one(selector)
                if desc_div:
                    # Remove any mark tags that might be present
                    for mark in desc_div.find_all('mark'):
                        mark.unwrap()
                    
                    # Clean up the text
                    text = desc_div.get_text(separator="\n").strip()
                    
                    # Remove extra whitespace and normalize line breaks
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    
                    # Join lines with proper spacing
                    text = "\n".join(lines)
                    
                    # Remove any duplicate newlines
                    text = "\n".join(line for line in text.split("\n") if line.strip())
                    
                    # Add proper spacing after bullet points
                    text = text.replace("\n•", "\n• ")
                    text = text.replace("\n-", "\n- ")
                    
                    return text
            
            return None
        except Exception as e:
            job_scraper_logger.warning(f"Error fetching job details: {str(e)}")
            return None

    async def process_job_card(self, card: BeautifulSoup) -> Optional[Dict]:
        """
        Process a single job card asynchronously.
        
        Args:
            card (BeautifulSoup): Job card element
            
        Returns:
            Optional[Dict]: Parsed job information
        """
        try:
            title_tag = card.find("h2", class_="jobTitle")
            link_tag = title_tag.find("a", href=True) if title_tag else None
            company_tag = card.find("span", attrs={"data-testid": "company-name"}) or card.find("span", class_="companyName")
            location_tag = card.find("div", attrs={"data-testid": "text-location"}) or card.find("div", class_="companyLocation")
            
            # Extract salary from card
            salary = self.extract_salary(card)
            
            # Get job link
            job_link = f"https://www.indeed.com{link_tag['href']}" if link_tag else None
            
            # Get full description using Selenium
            full_description = None
            if job_link:
                try:
                    full_description = await self.get_job_details_async(job_link)
                    # Go back to the search results page
                    self.driver.back()
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    job_scraper_logger.warning(f"Error fetching job description: {str(e)}")
            
            # If no salary found and we have a link, try detail page
            if not salary and job_link:
                try:
                    self.driver.get(job_link)
                    time.sleep(random.uniform(1, 2))
                    detail_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    salary = self.extract_salary(detail_soup, is_detail_page=True)
                    self.driver.back()
                    time.sleep(random.uniform(1, 2))
                except Exception as e:
                    job_scraper_logger.warning(f"Error fetching salary from detail page: {str(e)}")

            return {
                "title": title_tag.get_text(strip=True) if title_tag else None,
                "company": company_tag.get_text(strip=True) if company_tag else None,
                "location": location_tag.get_text(strip=True) if location_tag else None,
                "salary": salary,
                "link": job_link,
                "full_description": full_description
            }

        except Exception as e:
            job_scraper_logger.warning(f"Error parsing job card: {str(e)}")
            return None

    async def scrape_jobs_async(self, job_title: str = "data analyst", location: str = "Washington, DC", limit: int = 10) -> List[Dict]:
        """
        Scrape job listings from Indeed asynchronously.
        
        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            limit (int): Maximum number of jobs to scrape
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        jobs = []
        retry_count = 0
        current_page = 0

        try:
            self.setup_driver()
            
            # Now proceed with the search
            job_title_param = job_title.replace(" ", "+")
            location_param = location.replace(" ", "+")
            url = f"https://www.indeed.com/jobs?q={job_title_param}&l={location_param}"
            
            job_scraper_logger.info(f"Starting job search for: {job_title} in {location}")
            
            # Navigate to the search URL
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(random.uniform(3, 5))
            
            # Check for verification page
            if self.check_for_verification():
                if not self.handle_verification():
                    raise ScrapingError("Failed to complete verification")
            
            while len(jobs) < limit:
                if not self.wait_for_job_cards():
                    # Try refreshing the page once
                    job_scraper_logger.info("Refreshing page and trying again...")
                    self.driver.refresh()
                    time.sleep(random.uniform(3, 5))
                    if not self.wait_for_job_cards():
                        raise ScrapingError("No job results found or page failed to load properly")

                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                job_cards = soup.find_all("div", class_="job_seen_beacon")

                if not job_cards:
                    break  # No more jobs

                # --- Sequentially process job cards and stop early ---
                for card in job_cards:
                    job = await self.process_job_card(card)
                    if job:
                        jobs.append(job)
                    if len(jobs) >= limit:
                        break  # Stop processing further job cards

                if len(jobs) >= limit:
                    break  # Stop going to next pages

                # Find and click the "Next" button to go to the next page
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
                    if next_button and next_button.is_enabled():
                        next_button.click()
                        time.sleep(random.uniform(2, 4))
                    else:
                        break  # No more pages
                except Exception:
                    break  # No next button found, end of results

            return jobs

        except Exception as e:
            error_msg = f"Job scraping failed: {str(e)}"
            job_scraper_logger.error(error_msg)
            raise JobScraperError(error_msg) from e
        finally:
            if self.driver:
                self.driver.quit()
                job_scraper_logger.info("Chrome driver closed")
            if self.session:
                await self.session.close()

def scrape_jobs_api(role, location, output_path, limit=10):
    scraper = IndeedScraper()
    jobs = asyncio.run(scraper.scrape_jobs_async(role, location, limit=limit))
    with open(output_path, "w") as f:
        json.dump(jobs, f, indent=2)
    return jobs

async def main():
    """Main function to run the job scraper."""
    try:
        scraper = IndeedScraper()
        jobs = await scraper.scrape_jobs_async("data analyst", "Washington, DC", limit=10)

        with open("jobs.json", "w") as f:
            json.dump(jobs, f, indent=4)
        job_scraper_logger.info(f"Successfully saved {len(jobs)} job listings to jobs.json")

    except JobScraperError as e:
        job_scraper_logger.error(f"Job scraping failed: {str(e)}")
        raise
    except Exception as e:
        job_scraper_logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

