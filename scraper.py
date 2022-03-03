import requests
from requests.exceptions import MissingSchema, InvalidSchema
from bs4 import BeautifulSoup
from vars import HTML_HEAD
import base64
import pdfkit


class Scraper:

    def __init__(self):
        self.base_url = 'https://openclassrooms.com'

    @staticmethod
    def get_html_and_soup(url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        try:
            html = str(soup.find('main').find_all('div', attrs={'class': 'userContent js-userContent'})[0])
        except IndexError:
            pass
        return html, soup

    @staticmethod
    def get_final_html(course_url, course_html):
        course_title = ' '.join([elmt.title() for elmt in course_url.split('-') if 'http' not in elmt])
        course_intro = f"""
            <h1>{course_title}</h1>
            <h3>Lien du cours: <a href="{course_url}">{course_url}</a></h3>
        """
        return course_title, HTML_HEAD + course_intro + course_html

    @staticmethod
    def img_to_b64(img_url):
        image = base64.b64encode(requests.get(img_url).content).decode('utf-8')
        return image

    @staticmethod
    def convert_courses_as_pdf(final_html):
        pdfkit.from_string(final_html[1], f'{final_html[0]}.pdf', options={'images': '', 'lowquality': ''})

    def process_page(self, url):
        html, soup = self.get_html_and_soup(url)

        for img in soup.find_all('img'):
            try:
                b64 = self.img_to_b64(img.get('src'))
            except MissingSchema:
                if 'svg' or 'bundles' in img.get('src'):
                    b64 = self.img_to_b64(self.base_url + img.get('src'))
                else:
                    b64 = self.img_to_b64('https:' + img.get('src'))
            except InvalidSchema:
                continue
            file_ext = img.get('src').split('.')[-1]
            src = f'data:image/{file_ext};base64, {b64}'
            html = html.replace(img.get('src'), src)

        return html

    def get_all_links_from_course(self, url):
        html, soup = self.get_html_and_soup(url)
        all_links = []
        for section in soup.find_all('ol', attrs={'class': 'course-part-summary__list-content'}):
            links = [self.base_url + link.get('href') for link in section.find_all('a')]
            all_links += links
        return all_links

    def get_all_courses_as_html(self, links):
        html_courses = []
        for link in links:
            html_courses.append(self.process_page(link))
        final_html = HTML_HEAD + ''.join(html_courses)
        return final_html

    def scrap_course(self, course_url):
        links = self.get_all_links_from_course(course_url)
        course_html = self.get_all_courses_as_html(links)
        self.convert_courses_as_pdf(
            self.get_final_html(course_url, course_html)
        )
