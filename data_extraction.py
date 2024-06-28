import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

def extract(page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    query = "web OR software OR business OR teaching OR android OR developer"
    url = f'https://in.indeed.com/jobs?q={query}&l=india&start={page}'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def transform(soup):
    job_listings = []
    divs = soup.find_all('div', class_='job_seen_beacon')

    for items in divs:
        title_link = items.find('a', class_='jcs-JobTitle')
        if title_link:
            title = title_link.find('span').text.strip()
            link = "https://in.indeed.com" + title_link['href']
        else:
            title = "Title not found"
            link = ""

        company_location_div = items.find('div', class_='company_location')
        if company_location_div:
            location = company_location_div.find('div', {'data-testid': 'text-location'}).text.strip()
        else:
            location = "Location not found"

        company_span = items.find('span', {'data-testid': 'company-name'})
        company = company_span.text.strip() if company_span else "Company name not found"

        salary_div = items.find('div', class_='js-match-insights-provider-tvvxwd ecydgvn1')
        salary = salary_div.text.strip() if salary_div else ""

        description_ul = items.find('ul', style="list-style-type:circle;margin-top: 0px;margin-bottom: 0px;padding-left:20px;")
        if description_ul:
            description_items = description_ul.find_all('li')
            description = ' '.join([item.text.strip() for item in description_items])
        else:
            description = ""

        job_listings.append([title, company, salary, description, location, link])

    return job_listings

def save_to_csv(job_listings, output_csv='job3.csv'):
    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for job in job_listings:
            writer.writerow(job)

def extract_experience(description):
    if isinstance(description, str):
        if 'experience' in description.lower():
            experience_text = description.lower().split('experience')[0].strip()
            experience = ''.join(filter(str.isdigit, experience_text))
            return int(experience) if experience else 0
        else:
            return 0
    else:
        return 0

keywords = [
    'web', 'software', 'business', 'teaching', 'android', 'developer'
]

def extract_keyword(title):
    if isinstance(title, str):
        title_lower = title.lower()
        for keyword in keywords:
            if keyword in title_lower:
                return keyword.capitalize()
    return 'Other'

def process_and_save_data():
    output_csv = 'job3.csv'
    
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Company', 'Salary', 'Description', 'Location', 'Link'])

    for page in range(0, 10000, 10):  # Adjust the range for more pages
        print(f"Scraping page {page // 10 + 1}")
        soup = extract(page)
        job_listings = transform(soup)
        save_to_csv(job_listings, output_csv)

    unstructured_df = pd.read_csv(output_csv)
    unstructured_df['Experience'] = unstructured_df['Description'].apply(extract_experience)
    unstructured_df['Keyword'] = unstructured_df['Title'].apply(extract_keyword)
    unstructured_df.to_csv('updated_job_dataset3.csv', index=False)

    print("Data has been updated and saved to updated_job_dataset3.csv")

# Run the process
process_and_save_data()
