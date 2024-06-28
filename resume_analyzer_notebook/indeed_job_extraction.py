import requests
from bs4 import BeautifulSoup
import csv

def extract(page):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    name="Developer"
    url = f'https://in.indeed.com/jobs?q={name}&l=india&start={page}'
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


def save_to_csv(job_listings, output_csv='j.csv'):
    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for job in job_listings:
            writer.writerow(job)
    print(f"Data has been written to {output_csv}")

def main():
    output_csv = 'j.csv'
    

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Company', 'Salary', 'Description','city','url'])
    
    for page in range(0, 10000, 10):
        print(f"Scraping page {page // 10 + 1}")
        soup = extract(page)
        job_listings = transform(soup)
        save_to_csv(job_listings, output_csv)

if __name__ == "__main__":
    main()
