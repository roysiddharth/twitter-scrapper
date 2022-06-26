# Importing necessary libraries
import csv
from time import sleep
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys

def create_webdriver_instance():
    '''
    Creating the webdriver instance with the PATH variable containing the location of the
    chromedriver.exe on the local machine.
    can also use:

    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(ChromeDriverManager().install())
    '''
    PATH = '/home/sid/Anaconda/chromedriver'
    driver = webdriver.Chrome(PATH)
    return driver

def twitter_search(driver, search_term):
    '''
    Function to get the driver and search_term as arguments and type in the search_term in the
    automated browser window and press enter.
    '''
    url = 'https://twitter.com/search'
    driver.get(url)
    driver.maximize_window()
    sleep(10)

    search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)
    sleep(10)
    return True

def collect_cards(driver, lookback_limit = 30):
    '''
    Function to collect individual cards from the visible area of the HTML. lookback_limit is
    used to collect only the last certain number of cards on the page since Twitter pages are
    continuous and it might lead to repeating information.
    '''
    page_cards = driver.find_elements_by_xpath('//article[@data-testid="tweet"]')
    if len(page_cards) <= lookback_limit:
        return page_cards
    else:
        return page_cards[-lookback_limit:]

def generate_tweet_id(tweet):
    '''
    Function to generate unique tweet ids to prevent repetition of information.
    '''
    return ''.join(tweet).replace(" ", "")

def scroll_down_page(driver, last_position, num_seconds_to_load = 2, scroll_attempt = 0, max_attempts = 8):
    '''
    The function will try to scroll down the page and will check the current
    and last positions as an indicator. If the current and last positions are the same after `max_attempts`
    the assumption is that the end of the scroll region has been reached and the `end_of_scroll_region`
    flag will be returned as `True`
    '''
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt+1)
    last_position = curr_position
    return last_position, end_of_scroll_region

def extract_data_from_current_card(card):
    try:
        tweet_text = card.find_element_by_xpath('.//div[@data-testid="tweetText"]').text
    except exceptions.NoSuchElementException:
        tweet_text = ""
    try:
        date = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        date = ""
    try:
        likes = card.find_element_by_xpath('.//div[@data-testid="like"]').text
    except exceptions.NoSuchElementException:
        likes = ""
    try:
        retweets = card.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    except exceptions.NoSuchElementException:
        retweets = ""
    
    tweet = (date, tweet_text, likes, retweets)
    return tweet

def save_tweet_data_to_csv(records, filepath, mode='a+'):
    header = ['Date', 'Tweet', 'Likes', 'Retweets']
    with open(filepath, mode=mode, newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)
        if records:
            writer.writerow(records)

def main(search_term, filepath):
    save_tweet_data_to_csv(None, filepath, 'w')
    last_position = None
    end_of_scroll_region = False
    unique_tweets = set()

    driver = create_webdriver_instance()
    twitter_search_page_term = twitter_search(driver, search_term)
    if not twitter_search_page_term:
        return
    
    while not end_of_scroll_region:
        cards = collect_cards(driver)
        for card in cards:
            try:
                tweet = extract_data_from_current_card(card)
            except exceptions.StaleElementReferenceException:
                continue
            if not tweet:
                continue
            tweet_id = generate_tweet_id(tweet)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet)
                save_tweet_data_to_csv(tweet, filepath)
        last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
    driver.quit()

if __name__ == '__main__':
    '''
    Fill in the below two values with the filename of the csv file and the search term
    '''
    path = None
    term = None

    main(term, path)



