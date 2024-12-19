#importing libraries
import traceback
import os
import spacy
import traceback
import logging
logging.getLogger().setLevel(logging.CRITICAL)
import re
nlp = spacy.load('en_core_web_sm')
from dotenv import load_dotenv
load_dotenv()



# Function for preprocessing of text
def clean_text(text):
    doc = nlp(text)
    keywords = [str(token.lemma_).lower() for token in doc if token.pos_ not in ['PRON', 'PUNCT', 'SPACE'] and not token.is_stop and len(token.text)>1]
    clean_text = ' '.join(keywords)
    return clean_text


# Function for getting word token
def word_token(text):
    doc = nlp(text)
    keywords = [str(token.lemma_).lower() for token in doc if token.pos_ not in ['PRON', 'PUNCT', 'SPACE'] and not token.is_stop and len(token.text)>1]
    return keywords


#Function to remove number
def remove_number(text):
    no_digit_text = re.sub(r'\d+', '', text)
    return no_digit_text

#Function to extract phone number
def extract_valid_numbers_from_text(text):
    # Patterns to validate numbers with and without the +91 prefix
    with_prefix_pattern = r'\+91[6-9]\d{9}'
    without_prefix_pattern = r'[1-9]\d{9}'
    
    # Finding all matches in the text
    with_prefix_numbers = re.findall(with_prefix_pattern, text)
    without_prefix_numbers = re.findall(without_prefix_pattern, text)
    all_number = with_prefix_numbers + without_prefix_numbers
    for number in all_number:
        if number:
            break

    valid_number = str(number).strip()
    
    return valid_number