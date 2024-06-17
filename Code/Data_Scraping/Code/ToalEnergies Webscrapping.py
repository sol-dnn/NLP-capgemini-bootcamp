from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

def webscrapping_trustpilot(supplier, start_page=1, end_page=10):
    """
    Description:
    supplier: eni, totalenergies
    """

    # Initialize lists
    titles = []
    dates = []
    ratings = []
    comments = []
    replies = []

    # Define the format of your date string
    date_format = '%d %B %Y'  # %d is day, %B is full month name, %Y is year with century as a decimal number

    # Define a dictionary to map French month names to English month names
    french_to_english_month = {
        'janvier': 'January',
        'février': 'February',
        'mars': 'March',
        'avril': 'April',
        'mai': 'May',
        'juin': 'June',
        'juillet': 'July',
        'août': 'August',
        'septembre': 'September',
        'octobre': 'October',
        'novembre': 'November',
        'décembre': 'December'
    }
    
    #find returns the first HTML element found, whereas 
    #find_all returns a list of all elements matching the criteria

    for i in range(start_page, end_page + 1):
      url = 'https://fr.trustpilot.com/review/' + supplier + '.fr?'
      response = requests.get((f"{url}page={i}"))      #"https://fr.trustpilot.com/review/totalenergies.fr?page=3"
      web_page = response.text
      soup = BeautifulSoup(web_page, "html.parser") 

      for review in soup.find_all(class_ = 'paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_reviewCard__hcAvl'):    
          
          # Review titles
          title = review.find(class_ = "typography_heading-s__f7029 typography_appearance-default__AAY17")
          titles.append(title.getText())

          # Review dates
          date = review.find(class_ = "typography_body-m__xgxZ_ typography_appearance-default__AAY17")
          date = date.getText()[22:] # Remove the unnecessary part 'Date de l'expérience:'
          
          # Replace French month names with English month names in the date string
          for french_month, english_month in french_to_english_month.items():
              date = date.replace(french_month, english_month)     # We replace the french month string by english translation

          date = datetime.strptime(date, date_format) # Parse the date string into a datetime object
          dates.append(date)

          # Review ratings
          rating = review.find(class_ = "star-rating_starRating__4rrcf star-rating_medium__iN6Ty").findChild() 
            #get the first child element of the found element, 
          rating = rating["alt"][5:6] # Just get the number of stars
          ratings.append(int(rating)) # Convert rating to an integer to perform operations like mean rating

          # Review comments
          comment = review.find(class_ = "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn")
          # When there is no review text, append "" instead of skipping so that data remains in sequence with other review data
          if comment == None:
            comments.append("")
          else:
            comments.append(comment.getText())

          # Review replies
          reply = review.find(class_ = "typography_body-m__xgxZ_ typography_appearance-default__AAY17 styles_message__shHhX")
          # Same reasoning for the replies by the supplier
          if reply == None:
            replies.append("")
          else:
            replies.append(reply.getText())

    # Create final dataframe from lists
    df_reviews = pd.DataFrame(
       list(zip(dates, titles, comments, replies, ratings)),
       columns =['Date', 'Title', 'Comment', 'Reply', 'Rating']
    )
    
    #zip(dates, titles, comments, replies, ratings) represents a Python function that aggregates the elements from the five lists (dates, titles, comments, replies, ratings) into tuples. Each tuple contains one element from each of these lists, combined based on their corresponding index.

    # Output dataframe to csv file
    filename = 'Reviews_' + supplier
    df_reviews.to_csv(filename, index=False)

    print(f"DataFrame has been saved to {filename}")

    return df_reviews

def main(supplier):
    # Test function
    result = webscrapping_trustpilot(supplier)
    
    print("Result:\n", result)

if __name__ == "__main__":       #is a common idiom that's used to check whether the script is being run as the main
                             #program which means the script is being run directly (not imported as a module in another script)
    main(supplier='eni')
    main(supplier='totalenergies')
