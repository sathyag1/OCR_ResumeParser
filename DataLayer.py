#importing libraries
import psycopg2
import pandas.io.sql as psql
import io
import traceback
import logging
logging.getLogger().setLevel(logging.CRITICAL)
from dotenv import load_dotenv
import os
import locationtagger

load_dotenv()

import BusinessLayer as BL
import CommonLayer as CL


PG_USER = os.getenv('USER')
PG_PASSWORD = os.getenv('PASSWORD')
PG_HOST = os.getenv('HOST')
PG_PORT = os.getenv('PORT')
PG_DATABASE = os.getenv('DATABASE')




connection = psycopg2.connect(user = PG_USER, password = PG_PASSWORD, host = PG_HOST, port = PG_PORT, database = PG_DATABASE)

#getting master data list
skill_master_data = psql.read_sql('select sub_category_name from public.get_category_master_skills_vw', connection)

master_skills = " ".join(skill_master_data["sub_category_name"])

edu_master_data = psql.read_sql('select * from public.get_category_master_education_vw', connection)

degree_master_data = psql.read_sql('select * from public.get_category_master_eduction_degree_vw', connection)

job_title_mster_data = psql.read_sql('select * from public.get_category_master_job_title_vw', connection)



pg_loc = psql.read_sql('select * from public.get_category_master_city_vw', connection)



pg_loc_list = pg_loc["sub_category_name"].tolist()

indian_city_db = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Chennai', 'Kolkata', 'Surat', 'Pune', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri-Chinchwad', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik', 'Faridabad', 'Meerut', 'Rajkot', 'Kalyan-Dombivli', 'Vasai-Virar', 'Varanasi', 'Srinagar', 'Aurangabad', 'Dhanbad', 'Amritsar', 'Navi Mumbai', 'Allahabad', 'Howrah', 'Ranchi', 'Gwalior', 'Jabalpur', 'Coimbatore', 'Vijayawada', 'Jodhpur', 'Madurai', 'Raipur', 'Kota', 'Chandigarh', 'Guwahati', 'Solapur', 'Hubli–Dharwad', 'Mysore', 'Tiruchirappalli', 'Bareilly', 'Aligarh', 'Tiruppur', 'Gurgaon', 'Moradabad', 'Jalandhar', 'Bhubaneswar', 'Salem', 'Warangal', 'Mira-Bhayandar', 'Jalgaon', 'Guntur', 'Thiruvananthapuram', 'Bhiwandi', 'Saharanpur', 'Gorakhpur', 'Bikaner', 'Amravati', 'Noida', 'Jamshedpur', 'Bhilai', 'Cuttack', 'Firozabad', 'Kochi', 'Nellore', 'Bhavnagar', 'Dehradun', 'Durgapur', 'Asansol', 'Rourkela', 'Nanded', 'Kolhapur', 'Ajmer', 'Akola', 'Gulbarga', 'Jamnagar', 'Ujjain', 'Loni', 'Siliguri', 'Jhansi', 'Ulhasnagar', 'Jammu', 'Sangli-Miraj & Kupwad', 'Mangalore', 'Erode', 'Belgaum', 'Kurnool', 'Ambattur', 'Rajahmundry', 'Tirunelveli', 'Malegaon', 'Gaya', 'Udaipur', 'Karur', 'Kakinada', 'Davanagere', 'Kozhikode', 'Maheshtala', 'Rajpur Sonarpur', 'Bokaro', 'South Dum Dum', 'Bellary', 'Patiala', 'Gopalpur', 'Agartala', 'Bhagalpur', 'Muzaffarnagar', 'Bhatpara', 'Panihati', 'Latur', 'Dhule', 'Rohtak', 'Sagar', 'Korba', 'Bhilwara', 'Berhampur', 'Muzaffarpur', 'Ahmednagar', 'Mathura', 'Kollam', 'Avadi', 'Kadapa', 'Anantapuram[21]', 'Kamarhati', 'Bilaspur', 'Sambalpur', 'Shahjahanpur', 'Satara', 'Bijapur', 'Rampur', 'Shimoga', 'Chandrapur', 'Junagadh', 'Thrissur', 'Alwar', 'Bardhaman', 'Kulti', 'Nizamabad', 'Parbhani', 'Tumkur', 'Khammam', 'Uzhavarkarai', 'Bihar Sharif', 'Panipat', 'Darbhanga', 'Bally', 'Aizawl', 'Dewas', 'Ichalkaranji', 'Karnal', 'Bathinda', 'Jalna', 'Eluru', 'Barasat', 'Kirari Suleman Nagar', 'Purnia', 'Satna', 'Mau', 'Sonipat', 'Farrukhabad', 'Durg', 'Imphal', 'Ratlam', 'Hapur', 'Arrah', 'Anantapur', 'Karimnagar', 'Etawah', 'Ambarnath', 'North Dum Dum', 'Bharatpur', 'Begusarai', 'New Delhi', 'Gandhidham', 'Baranagar', 'Tiruvottiyur', 'Pondicherry', 'Sikar', 'Thoothukudi', 'Rewa', 'Mirzapur', 'Raichur', 'Pali', 'Ramagundam', 'Silchar', 'Haridwar', 'Vijayanagaram', 'Tenali', 'Nagercoil', 'Sri Ganganagar', 'Karawal Nagar', 'Mango', 'Thanjavur', 'Bulandshahr', 'Uluberia', 'Katni', 'Sambhal', 'Singrauli', 'Nadiad', 'Secunderabad', 'Naihati', 'Yamunanagar', 'Bidhannagar', 'Pallavaram', 'Bidar', 'Munger', 'Panchkula', 'Burhanpur', 'Kharagpur', 'Dindigul', 'Gandhinagar', 'Hospet', 'Nangloi Jat', 'Malda', 'Ongole', 'Deoghar', 'Chhapra', 'Puri', 'Haldia', 'Khandwa', 'Nandyal', 'Morena', 'Amroha', 'Anand', 'Bhind', 'Bhalswa Jahangir Pur', 'Madhyamgram', 'Bhiwani', 'Berhampore', 'Ambala', 'Morbi', 'Fatehpur', 'Raebareli', 'Khora, Ghaziabad', 'Chittoor', 'Bhusawal', 'Orai', 'Bahraich', 'Phusro', 'Vellore', 'Mehsana', 'Raiganj', 'Sirsa', 'Danapur', 'Serampore', 'Sultan Pur Majra', 'Guna', 'Jaunpur', 'Panvel', 'Shivpuri', 'Surendranagar Dudhrej', 'Unnao', 'Chinsurah', 'Alappuzha', 'Kottayam', 'Machilipatnam', 'Shimla', 'Midnapore', 'Adoni', 'Udupi', 'Katihar', 'Proddatur', 'Budaun', 'Mahbubnagar', 'Saharsa', 'Dibrugarh', 'Jorhat', 'Hazaribagh', 'Hindupur', 'Nagaon', 'Hajipur', 'Sasaram', 'Giridih', 'Bhimavaram', 'Port Blair', 'Kumbakonam', 'Bongaigaon', 'Raigarh', 'Dehri', 'Madanapalle', 'Siwan', 'Bettiah', 'Ramgarh', 'Tinsukia', 'Guntakal', 'Srikakulam', 'Motihari', 'Dharmavaram', 'Medininagar', 'Gudivada', 'Phagwara', 'Pudukkottai', 'Hosur', 'Narasaraopet', 'Suryapet', 'Miryalaguda', 'Anantnag', 'Tadipatri', 'Karaikudi', 'Kishanganj', 'Gangavathi', 'Jamalpur', 'Ballia', 'Kavali', 'Tadepalligudem', 'Amaravati', 'Buxar', 'Tezpur', 'Jehanabad', 'Aurangabad', 'Gangtok', 'Vasco Da Gama']

indian_city_loc = indian_city_db + pg_loc_list


indian_loc = []
for city in indian_city_loc:
    indian_loc.append(city.lower())


edu_master_data =edu_master_data["master_category_description"].tolist()
degree_master_data = degree_master_data['master_category_description'].tolist()

total_edu = edu_master_data + degree_master_data

total_edu = [x.lower() for x in total_edu]

job_title_master_list = job_title_mster_data['sub_category_name']

clean_job_title = [job_title.lower().strip() for job_title in job_title_master_list]


#Function to get location
def extract_location(text):
    entities = locationtagger.find_locations(text = text)
    location=entities.cities
    # print("loc, ", location )
    location_tag = [x for x in location if x in  indian_loc]
    token = CL.word_token(text)
    # print("text: ", token)
    location_match = [x for x in token if x in  indian_loc]
    # print("match: ", location_match)
    alll_locations = location_tag + location_match
    final_location = list(set(alll_locations))
                
    return final_location