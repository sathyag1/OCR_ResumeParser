#importing libraries
import traceback
import os
import mammoth
import pdfkit
import requests
import fitz
import spacy
import fitz
import io
import traceback
import logging
logging.getLogger().setLevel(logging.CRITICAL)
from dotenv import load_dotenv

from datetime import datetime, date
import difflib
import re

#Library_addition
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('maxent_ne_chunker')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('brown')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('treebank')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')


#importing resume parser
from resume_parser import resumeparse



load_dotenv()
import DataLayer as DL
import CommonLayer as CL


# Getting Path
path = "/usr/bin/wkhtmltopdf"
# path = r"wkhtmltopdf.exe"

# Sept to  Sep function
def custom_strptime(date_str, date_format):
    
    month_translations = {
        'sept': 'sep',
        
    }
    
    
    for k, v in month_translations.items():
        date_str = date_str.lower().replace(k, v)

    return date_str

#Function to check valid_email

def is_valid_email(email):
    # A basic regular expression to check if the email format is correct
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)

#processed master data skill
processed_master_skills = CL.word_token(DL.master_skills)

#education year pattern
year_pattern = r"\b(19\d{2}|20(?:0\d|1[0-9]))\b"

#Dictionary for extracting keyword

keywords_dict = {"skills": ["competen", "skill", "proficiency", "expertise", "software", "technology"], #, "experience", "qualification"
            "experience": ["experience", "working", "responsibilities", "career", "company", "employment", "internship"],
            "education": ["education", "qualification", "academic"],
            "address": ["address"]
           }


#Extraction Keyword based function
def findkeywordcontent(resume_content, keyword, maxwords=4): #blocks
    
    doc = fitz.Document(stream=resume_content, filetype="pdf")
    blocks = []
    for page in doc.pages():
        pagecontent = page.get_text(option="dict")
        pageblocks = pagecontent["blocks"]
        blocks.extend(pageblocks)
    
    keyword = str(keyword).lower().strip()
    keywordfound = False
    keywordtext = ""
    for block in blocks:
        if "lines" in block:
            lines = block["lines"]
            for line in lines:
                if "spans" in line:
                    spans = line["spans"]
                    linetext = ""
                    linefonts = []
                    lineflags = []
                    linecolor = []
                    linesizes = []
                    for span in spans:
                        if "text" in span:
                            linetext += span["text"]
                            linefonts.append(span["font"])
                            lineflags.append(span["flags"])
                            linecolor.append(span["color"])
                            linesizes.append(span['size'])
                    if keywordfound == True:

                        currentfonts = set(linefonts)
                        currentflags = set(lineflags)
                        currentcolor = set(linecolor)
                        currentsizes = set(linesizes)
                        if (
                            currentfonts == keywordfonts
                            and currentflags == keywordflags
                            and currentcolor == keywordcolor
                            and currentsizes == keywordsizes
                        ):
                            return keywordtext.strip()
                        keywordtext += linetext + "\n"

                    if (
                        keyword in linetext.lower()
                        and len(linetext.split()) < maxwords
                        and keywordfound == False
                    ):
                        keywordfound = True
                        keywordtext = ""
                        keywordfonts = set(linefonts)
                        keywordflags = set(lineflags)
                        keywordcolor = set(linecolor)
                        keywordsizes = set(linesizes)
    return keywordtext.strip()


#Resume parser extraction
def extracting_resume_dict(resume_path, para):

    
    try:
        json_object = {}
        
        resume_dict = resumeparse.read_file(resume_path)
        full_text = para["full_text"]
        for key, value in resume_dict.items():
            if key == "degree" and  isinstance(value, list):
                key = "education"
                emp_list = []
                edu_para = para["total_education"]
                # print(edu_para)
                pairs = re.findall(r'(?=(\b[^ ]+ [^ ]+\b))', edu_para)

                
                result = [difflib.get_close_matches(x.lower().strip(), edu_para.split() + pairs, n=3, cutoff=0.5) for x in DL.total_edu]

                matches = [r[0] for r in result if len(r)> 0]

                matches = [x for x in matches if x in DL.total_edu]

                value = [x.lower() for x in value]
                for i in matches:
                    if i not in value:
                        value.append(i)

                for element in value:
                    new_dict = {}
                    inner_key1 = "education"
                    inner_key2 = "account_login_id"
                    inner_key3 = "field_of_study"
                    inner_key4 = "education_start_date"
                    inner_key5 = "education_end_date"
                    inner_key6 = "education_institute_city"
                    inner_key7 = "percentage_range"

                    new_dict[inner_key1] = CL.clean_text(element)
                    new_dict[inner_key2] = ""
                    new_dict[inner_key3] = ""
                    new_dict[inner_key4] = re.findall(year_pattern, para["total_education"])
                    new_dict[inner_key5] = re.findall(year_pattern, para["total_education"])
                    new_dict[inner_key6] = DL.extract_location(para["total_education"])
                    new_dict[inner_key7] = ""
                    emp_list.append(new_dict)
                json_object[key] = emp_list

            elif key == "Companies worked at" and isinstance(value, list):
                    key = "experiences"
                    emp_list = []
                    value = list(set(value))
                    for element in value:
                        new_dict = {}
                        inner_key1 = "company_name"
                        inner_key2 = "job_title"
                        inner_key3 = "job_start_date"
                        inner_key4 = "job_end_date"
                        inner_key5 = "performed_job_responsibilities"
                        
                        element = CL.remove_number(CL.clean_text(element))
                        if (len(element) != 0) or (element != " "):
                            new_dict[inner_key1] = element
                        designation_cleaned = [x.lower() for x in resume_dict["designition"] ]
                        designation_filtered = [x for  x in designation_cleaned if x in DL.clean_job_title] + resume_dict["designition"]
                        new_dict[inner_key2] = list(set(designation_filtered))
                        new_dict[inner_key3] = ""
                        new_dict[inner_key4] = ""
                        emp_list.append(new_dict)
                    json_object[key] = emp_list

            elif key == "skills" and isinstance(value, list):
                key = "preferred_skill"
                emp_list = []
                skill_para = para["total_skills"]
               
                extra_skills = CL.word_token(skill_para)
                filterred_skill = list(filter(lambda x: x in extra_skills, processed_master_skills))
              
                for i in filterred_skill:
                    if i not in value:
                        value.append(i)

                value = [CL.remove_number(CL.clean_text(x)) for x in value]
                value = [x for x in value if (len(x)> 0) if x != " "]
               
                for element in list(set(value)):
                        new_dict = {}
                        inner_key = "preferred_skill_name"
                        new_dict[inner_key] = element
                        emp_list.append(new_dict)

                json_object[key] = emp_list
            elif key == "name" and value is not None:
                key = "full_name"
                json_object[key] = value.lower().strip()



            elif key == "email" : #and value is not None
                key = "email_id"
                try:
                    if value:
                        email = value.lower().strip()
                        if is_valid_email(email):
                            json_object[key] = email

                        else:
                            all_email = get_emails(full_text)
                            if all_email:
                                for each_email in all_email:
                                    if is_valid_email(each_email):
                                        json_object[key] = each_email
                                        break
                                    else:
                                        json_object[key] = " "
                            else:
                                json_object[key] = " "
                    else:
                        all_email = get_emails(full_text)
                        if all_email:
                            for each_email in all_email:
                                if is_valid_email(each_email):
                                    json_object[key] = each_email
                                    break

                                else:
                                        json_object[key] = " "
                        else:
                            json_object[key] = " "
                except:
                    json_object[key] = " "
                

            elif key == "phone" and value is not None:
                key = "primary_phone_number"
                
                try:
                    value = value.strip()
                    if value:
                        if (len(value.strip())) >= 10:
                            json_object[key] = value.strip()
                        else:
                            ph_number = CL.extract_valid_numbers_from_text(full_text)
                            json_object[key] = ph_number

                    else:
                        ph_number = CL.extract_valid_numbers_from_text(full_text)
                        json_object[key] = ph_number

                except Exception as e:
                    print(e)
                    json_object[key] = value

            elif key == "total_exp" and value is not None:
                key = "total_work_experiance"
                json_object[key] = str(value).lower().strip()

            else:
                pass

    except Exception as e:
        print(traceback.format_exc())
        json_object = {}
        print('Exception ----------', e)
             
    return json_object


#Function to extract email
def get_emails(x):
    re_email = re.compile(r'\b[a-zA-Z0-9_.]+@[a-zA-Z]+[.][a-zA-Z]+\b')
    return re_email.findall(x)


#Getting token from paragraph
def getting_value(text):
    value_list = CL.word_token
    return value_list

#Paragraph extraction function
def extraction_para_dict(keywords, resume_path):
    
    try:
        if resume_path[-3:] == "pdf":
            response = requests.get(resume_path)
            resume_content = response.content
            doc_full = fitz.Document(stream=resume_content, filetype="pdf")
            full_text = " "
            for i in doc_full.pages():
                full_text += i.get_text()
            full_text = CL.clean_text(full_text)


            try:

                date_regexes = [
                    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Sept(?:ember)?|Nov(?:ember)?|Dec(?:ember)?)[,]?\s?\d{4}\b",  # Matches dates in format Month YYYY
                    r"\b\d{1,2}[/:]\d{4}\b",  # Matches dates in format DD/YYYY or MM/YYYY
                    r"\b\d{1,2}[/:]\d{1,2}[/:]\d{4}\b",  # Matches dates in format DD/MM/YYYY
                    r"\b\d{1,2}[:]\d{1,2}[:]\d{4}\b",  # Matches dates in format DD:MM:YYYY
                    r"\b\d{1,2}[-]\d{1,2}[-]\d{4}\b",
                    r"\b\d{1,2}[-.]\d{1,2}[-.]\d{4}\b",
                    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Sept(?:ember)?|Nov(?:ember)?|Dec(?:ember)?)[, ]?\s\d{1,2}(?:st|nd|rd|th)?[, ]?\s\d{4}\b"


                ]

                # Define regular expression for dob pattern
                dob_regex = r"\b(date of birth|dob | d.o.b | birthday | date birth | birth)[: -]*"
                matched_dates = re.findall("(" + "|".join(date_regexes) + ")", full_text, re.IGNORECASE)
               
                # Convert matched dates to date objects and keep track of original strings
                date_objects = []
                original_strings = []
                date_formats = [
                                    '%d/%m/%Y',
                                    '%B %Y',
                                    '%b %Y',
                                    '%B, %Y',
                                    '%b,%Y',
                                    '%b/%Y',
                                    '%b-%Y',
                                    '%d-%m-%Y',
                                    '%d:%m:%Y',
                                    '%b.%Y',
                                    '%d.%m.%Y',
                                    '%B %d, %Y',
                                    '%B %d %Y',
                                    '%B, %d, %Y'
                                ]
                some_pattern = ["nd", "rd", "th", "st"]
                for matched_date in matched_dates:
                    # print("Dates, ", matched_date )
                    if any(x in matched_date for x in some_pattern):
                        matched_date = matched_date.replace("nd", "").replace("st", "").replace("rd", "").replace("th", "")
                        matched_dates.append(matched_date)
                    else:
                        pass
                    
          
                    for date_regex in date_regexes:
                        match = re.search(date_regex, matched_date, re.IGNORECASE)
                        if match:
                            date_str = match.group(0)
                            for matched_date in matched_dates:
                                for date_format in date_formats:
                                    try:
                                        if matched_date.split()[0]== "sept":
                                            matched_date = custom_strptime(matched_date, "%b %Y")

                                        date_obj = datetime.strptime(matched_date, date_format).date()
                                        date_objects.append(date_obj)
                                        original_strings.append(matched_date)
                                        break  # Exit the inner loop if a match is found
                                    except ValueError:
                                        pass
                
                            date_objects.append(date_obj)
                            original_strings.append(matched_date)

                if date_objects:
                    smallest_date = min(date_objects)
                    # Find the original string for the smallest date
                    original_string = original_strings[date_objects.index(smallest_date)]

                else:
                    smallest_date = ''
                    original_string = ''
                    
                if original_string != '':
                    # Find the original string for the smallest date
                    original_string = original_strings[date_objects.index(smallest_date)]


                #Find the date of birth string, if it exists
                dob_string = re.search(dob_regex, full_text, re.IGNORECASE)
                try:
                    if dob_string:
                        dob_string = dob_string.group(0)
                        dob = original_string
                    elif (date.today() - smallest_date).days > 365.25 * 18:
                        dob = original_string

                    else:
                        dob = " "

                except Exception as e:
                    print(traceback.format_exc())
                    print("Exception-------", e)

                    dob = " "

            except Exception as e:
                print("Exception-------", e)
                print(traceback.format_exc())
                dob = " "

            skill= "" 
            experience = ""
            education = ""
            address = ""
            filename= ""

            temp_skill = ""
            temp_exp = ""
            temp_edu = ""
            temp_address= ""
            for key, values in keywords.items(): 
                for value in values:
                    text_ = findkeywordcontent(resume_content, value) 

                    if key == "skills": 
                        temp_skill+= text_


                    elif key == "experience": 
                        temp_exp += text_

                    elif key == "education": 
                        temp_edu += text_

                    elif key == "address": 
                        temp_address += text_

                    

            filename+=resume_path
            skill+=CL.clean_text(temp_skill)
            experience+=CL.clean_text(temp_exp)
            education+=CL.clean_text(temp_edu)
            address+=CL.clean_text(temp_address)
            date_of_birth = dob
            para_dict= {"file": filename, "total_skills": skill, "total_experience": experience, "total_education": education, "address": address, "date_of_birth": date_of_birth, "full_text": full_text}
        elif resume_path[-4:] == "docx":
            try:
                content = requests.get(resume_path).content
                document = io.BytesIO(content)
                print("io success")
                result = mammoth.convert_to_html(document)
                print("mammoth sucess")
                config = pdfkit.configuration(wkhtmltopdf=path)
                print("path sucess")
                resume_content = pdfkit.from_string(result.value, configuration =config)
                print("wkdocx2pdf success")
            except Exception as e:
                print("word 2 word")
                print("Exception-------", e)

            doc_full = fitz.Document(stream=resume_content, filetype="pdf")
            full_text = " "
            for i in doc_full.pages():
                full_text += i.get_text()
            full_text = CL.clean_text(full_text)

            try:

                date_regexes = [
                    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Sept(?:ember)?|Nov(?:ember)?|Dec(?:ember)?)[,]?\s?\d{4}\b",  # Matches dates in format Month YYYY
                    r"\b\d{1,2}[/:]\d{4}\b",  # Matches dates in format DD/YYYY or MM/YYYY
                    r"\b\d{1,2}[/:]\d{1,2}[/:]\d{4}\b",  # Matches dates in format DD/MM/YYYY
                    r"\b\d{1,2}[:]\d{1,2}[:]\d{4}\b",  # Matches dates in format DD:MM:YYYY
                    r"\b\d{1,2}[-]\d{1,2}[-]\d{4}\b",
                    r"\b\d{1,2}[-.]\d{1,2}[-.]\d{4}\b",
                    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Sept(?:ember)?|Nov(?:ember)?|Dec(?:ember)?)[, ]?\s\d{1,2}(?:st|nd|rd|th)?[, ]?\s\d{4}\b"


                ]

                # Define regular expression for dob pattern
                dob_regex = r"\b(date of birth|dob | d.o.b | birthday | date birth | birth)[: -]*"
                matched_dates = re.findall("(" + "|".join(date_regexes) + ")", full_text, re.IGNORECASE)
               
                # Convert matched dates to date objects and keep track of original strings
                date_objects = []
                original_strings = []
                date_formats = [
                                    '%d/%m/%Y',
                                    '%B %Y',
                                    '%b %Y',
                                    '%B, %Y',
                                    '%b,%Y',
                                    '%b/%Y',
                                    '%b-%Y',
                                    '%d-%m-%Y',
                                    '%d:%m:%Y',
                                    '%b.%Y',
                                    '%d.%m.%Y',
                                    '%B %d, %Y',
                                    '%B %d %Y',
                                    '%B, %d, %Y'
                                ]
                some_pattern = ["nd", "rd", "th", "st"]
                for matched_date in matched_dates:
                    # print("Dates, ", matched_date )
                    if any(x in matched_date for x in some_pattern):
                        matched_date = matched_date.replace("nd", "").replace("st", "").replace("rd", "").replace("th", "")
                        matched_dates.append(matched_date)
                    else:
                        pass
                    
          
                    for date_regex in date_regexes:
                        match = re.search(date_regex, matched_date, re.IGNORECASE)
                        if match:
                            date_str = match.group(0)
                            for matched_date in matched_dates:
                                for date_format in date_formats:
                                    try:
                                        if matched_date.split()[0]== "sept":
                                            matched_date = custom_strptime(matched_date, "%b %Y")

                                        date_obj = datetime.strptime(matched_date, date_format).date()
                                        date_objects.append(date_obj)
                                        original_strings.append(matched_date)
                                        break  # Exit the inner loop if a match is found
                                    except ValueError:
                                        pass
                
                            date_objects.append(date_obj)
                            original_strings.append(matched_date)

                if date_objects:
                    smallest_date = min(date_objects)
                    # Find the original string for the smallest date
                    original_string = original_strings[date_objects.index(smallest_date)]

                else:
                    smallest_date = ''
                    original_string = ''
                    
                if original_string != '':
                    # Find the original string for the smallest date
                    original_string = original_strings[date_objects.index(smallest_date)]


                #Find the date of birth string, if it exists
                dob_string = re.search(dob_regex, full_text, re.IGNORECASE)
                try:
                    if dob_string:
                        dob_string = dob_string.group(0)
                        dob = original_string
                    elif (date.today() - smallest_date).days > 365.25 * 18:
                        dob = original_string

                    else:
                        dob = " "

                except Exception as e:
                    print(traceback.format_exc())
                    print("Exception-------", e)

                    dob = " "

            except Exception as e:
                print("Exception-------", e)
                print(traceback.format_exc())
                dob = " "

       

            skill= "" 
            experience = ""
            education = ""
            address = ""
            filename= ""

            temp_skill = ""
            temp_exp = ""
            temp_edu = ""
            temp_address= ""
            for key, values in keywords.items(): 
                for value in values:
                    text_ = findkeywordcontent(resume_content, value) 

                    if key == "skills": 
                        temp_skill+= text_


                    elif key == "experience": 
                        temp_exp += text_

                    elif key == "education": 
                        temp_edu += text_

                    elif key == "address": 
                        temp_address += text_

            filename+=resume_path
            skill+=CL.clean_text(temp_skill)
            experience+=CL.clean_text(temp_exp)
            education+=CL.clean_text(temp_edu)
            address+=CL.clean_text(temp_address)
            date_of_birth = dob


            para_dict= {"file": filename, "total_skills": skill, "total_experience": experience, "total_education": education, "address": address, "date_of_birth": date_of_birth,  "full_text": full_text}

        else:
            para_dict = {"file": " ", "total_skills": " ", "total_experience": " ", "total_education": " ", "address": " ", "date_of_birth" : " " , "full_text": " "}

    except Exception as e:
      
        print("Exception-------", e)
        para_dict = {"file": " ", "total_skills": " ", "total_experience": " ", "total_education": " ", "address": " ", "date_of_birth" : " ", "full_text": " "}
    
    return para_dict
















