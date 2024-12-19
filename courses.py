import requests
from bs4 import BeautifulSoup
import os

def scrape_programs(url, output_file):
    try:        
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        programs = soup.find_all('li', class_='programslist--item')

        with open(output_file, 'a', encoding='utf-8') as file:
            file.write(f"Programs from: {url}\n")
            file.write("-" * 50 + "\n")
            for program in programs:              
                program_name = program.find('span', class_='programslist__pid').get_text(strip=True)                
                credential = program.find('span', class_='programslist__credential')
                credential = credential.get_text(strip=True) if credential else "None"
                
                program_format = program.find('span', class_='programslist__format')
                program_format = program_format.get_text(strip=True) if program_format else "None"                
                link = program.find('a', class_='programslist--link')
                href_link = link['href'] if link and 'href' in link.attrs else "None"
                
                file.write(f"Program Name: {program_name}\n")
                file.write(f"Credential: {credential}\n")
                file.write(f"Format: {program_format}\n")
                file.write(f"Link: {href_link}\n")
                file.write("-" * 50 + "\n")
            file.write("\n")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing {url}: {e}")


def scrape_courses(program_url, output_file):
    try:        
        response = requests.get(program_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        courses_table = soup.find('table', id='programmatrix')
        
        if not courses_table:
            print(f"No courses table found at {program_url}. Skipping...")
            return 
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(f"Courses for Program: {program_url}\n")
            file.write("-" * 50 + "\n")
                        
            for row in courses_table.find_all('tr')[1:]: 
                course_number_cell = row.find('td', class_='course_number')
                
                if course_number_cell:                    
                    course_link_tag = course_number_cell.find('a')
                    if course_link_tag:
                        course_link = course_link_tag['href']
                        course_number = course_link_tag.get_text(strip=True)
                    else:                        
                        course_link = "None"
                        course_number = course_number_cell.get_text(strip=True)
                else:
                    continue 

                
                course_name_tag = row.find('td', class_='peekaboo').find('strong', class_='course_name')
                course_name = course_name_tag.get_text(strip=True) if course_name_tag else "None"
                                
                file.write(f"Course Number: {course_number}\n")
                file.write(f"Course Link: {course_link}\n")
                file.write(f"Course Name: {course_name}\n")
                file.write("-" * 50 + "\n")
                
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while accessing {program_url}: {e}")

if __name__ == "__main__":    
    target_urls = [
        "applied-natural-sciences",
        "business-media",
        "computing-it",
        "engineering",
        "health-sciences",
        "trades-apprenticeships"
    ]
    
    base_url = "https://www.bcit.ca/study/"
    
    programs_file = "programs_list.txt"
    
    open(programs_file, 'w').close()
    
    for path in target_urls:
        full_url = base_url + path + "/programs/"
        print(f"Scraping programs from: {full_url}")
        scrape_programs(full_url, programs_file)
    
    with open(programs_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    program_links = [line.split(": ")[1].strip() for line in lines if line.startswith("Link:") and line.split(": ")[1].strip() != "None"]
    
    os.makedirs("courses", exist_ok=True)
    
    for link in program_links:
        program_name = link.split('/')[-2]  
        output_file = f"courses/{program_name}_courses.txt"
        print(f"Scraping courses from: {link + '#courses'}")
        scrape_courses(link, output_file)

    print("Scraping completed.")
