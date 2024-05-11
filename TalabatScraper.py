from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import requests
import numpy as np
import time
import os

class TalabatScraper:
    """
    A class for scraping menu data from Talabat website.

    Methods:
        getMenuCategories(html): Extracts the menu categories from the HTML content.
        getCategoryName(MenuCategory): Extracts the name of a menu category.
        getMenuItems(MenuCategory): Extracts the menu items from a menu category.
        scrape_picture(MenuItem, name, RestaurantName, path=None): Scrapes the picture of a menu item and saves it to a file.
        scrapeMenuItem(MenuItem): Scrapes the details of a menu item.
        scrapeMenu(html, RestaurantName, path=None): Scrapes the menu from the provided HTML and returns a pandas DataFrame with the menu data.
    """

    def getMenuCategories(self, html):
        """
        Extracts the menu categories from the HTML content.

        Args:
            html (str): The HTML content of the menu page.

        Returns:
            list: A list of BeautifulSoup objects representing the menu categories.
        """
        soup = BeautifulSoup(html, 'html.parser')
        MenuCategories = soup.select('body>div#__next>div[data-testid="app-component"]>div>div>div>div>div.mt-2>div> div.row>div.col-md-11>div.row>div.col-sm-11>div.sc-5b556770-0>div')
        return MenuCategories
    
    def getCategoryName(self, MenuCategory):
        """
        Extracts the name of a menu category.

        Args:
            MenuCategory (BeautifulSoup): The BeautifulSoup object representing the menu category.

        Returns:
            str: The name of the menu category.
        """
        CategoryName = MenuCategory.select('div.accordion>div.text-wrap>h4')[0].text
        return CategoryName

    def getMenuItems(self, MenuCategory):
        """
        Extracts the menu items from a menu category.

        Args:
            MenuCategory (BeautifulSoup): The BeautifulSoup object representing the menu category.

        Returns:
            list: A list of BeautifulSoup objects representing the menu items.
        """
        MenuItems = MenuCategory.select('div>div.content.open>div>div')
        return MenuItems
    
    def scrape_picture(self, MenuItem, name, RestaurantName, path=None):
        """
        Scrapes the picture of a menu item and saves it to a file.

        Args:
            MenuItem (BeautifulSoup): The menu item element to scrape the picture from.
            name (str): The name of the menu item.
            RestaurantName (str): The name of the restaurant.
            path (str, optional): The path to save the picture file. Defaults to None. If not provided, the current working directory will be used.

        Returns:
            None
        """
        if path is None:
            path = os.getcwd()
            path = os.path.join(path, RestaurantName)
        else:
            path = os.path.join(path, RestaurantName)
        picturelink = MenuItem.select("div>div>div>div>div>div>img")[0]['src']
        try:
            img_data = requests.get(picturelink).content 
            with open(f"{path}\{name}.jpg", 'wb') as handler: 
                handler.write(img_data) 
        except:
            pass
        
    def scrapeMenuItem(self, MenuItem):
        """
        Scrapes the details of a menu item.

        Args:
            MenuItem (BeautifulSoup): The BeautifulSoup object representing the menu item.

        Returns:
            tuple: A tuple containing the name, description, and price of the menu item.
        """
        name = MenuItem.select('div.item-name>div:nth-child(1)')[0].text
        if name[-1] == '.':
            name = name[:-1]
        description = MenuItem.select('div.item-name>div:nth-child(2)')[0].text
        try:
            price = float(MenuItem.select('div.price-rating>div>div>span.currency')[0].text)
        except:
            price = np.nan

        return name, description, price
    
    def scrapeMenu(self, html, RestaurantName, path=None):
        """
        Scrapes the menu from the provided HTML and returns a pandas DataFrame with the menu data.

        Args:
            html (str): The HTML content of the menu page.
            RestaurantName (str): The name of the restaurant.
            path (str, optional): The path to save the scraped images. Defaults to None.

        Returns:
            pandas.DataFrame: A DataFrame containing the scraped menu data with columns: 'Category', 'ItemName', 'Description', 'Price'.
        """
        if path is None:
            path = os.getcwd()
        try:
            os.mkdir(os.path.join(path, RestaurantName))
        except:
            pass
        categories = []
        itemNames = []
        descriptions = []
        prices = []

        MenuCategories = self.getMenuCategories(html)
        for MenuCategory in MenuCategories:
            MenuItems = self.getMenuItems(MenuCategory)
            MenuCategoryName = self.getCategoryName(MenuCategory)
            for MenuItem in MenuItems:
                name, description, price = self.scrapeMenuItem(MenuItem)
                self.scrape_picture(MenuItem, name, RestaurantName, path)
                categories.append(MenuCategoryName)
                itemNames.append(name)
                descriptions.append(description)
                prices.append(price)
        dataframe = pd.DataFrame({'Category': categories, 'ItemName': itemNames, 'Description': descriptions, 'Price': prices})
        return dataframe



def get_html(url):

    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(url)
    max_scrolls = 100
    scroll_count = 0
    i=0
    while (scroll_count < max_scrolls) and (i<=10):
        browser.execute_script(f"window.scrollTo(0, {i/10}*document.body.scrollHeight);")
        time.sleep(2)  
        i+=1
        scroll_count += 1
    html = browser.page_source
    
    return html

