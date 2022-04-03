
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime as dt

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),

        # Added hemispheres dictionary by callig a function that returns 
        # List of dictionaries that contains links and titles
        "hemispheres": hemispheres_scrape(browser)
    }

    browser.quit()

    return data

def mars_news(browser):
    
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Try /except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Find the relative image url
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
   
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts():

    # Add try / except for error handling
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    
    except BaseException:
        return None

    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    return df.to_html()

# New function that scrapes images and tiles for hemisphers of Mars
# Returns a list of dictionaries
# Copied from the end of Mission_to_Mars_Challenge.py
# Passing the browser object to the function is required for browser to work

def hemispheres_scrape(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles. (Note, will be a list of dictionaries)
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    # Convert the webpage into an HTML object and then parse it using soup
    hemi_html = browser.html
    hemi_parsed = soup(hemi_html, "html.parser")

    #3 continued...

    # Find each hemishphere section with its hyper link tot he full image.
    hemi_loc_list = hemi_parsed.find_all("div", class_="description")

    # Create a loop that goes through each of the sections, finds the link to next page
    # goes to the next page, finds the jpg address and description, and adds it to the image list
    for hemi in hemi_loc_list:

        # Set the address of the new site 
        hemi_address = url + hemi.find("a")["href"]

        # Send the browerse to the new site
        browser.visit(hemi_address)

        # Parse the new site
        html = browser.html
        img_des = soup(html, "html.parser")

        # Find the image address for current hemispher jpg
        img_url = url + img_des.find("div",class_="downloads").find("a")["href"]

        # Find the title
        title = img_des.find("h2",class_="title").text

        # add to the list
        hemisphere_image_urls.append({"img_url": img_url, "title":title})

    # Modified to return a list of dictionaries to the calling stack
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())