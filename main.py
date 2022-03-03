from scraper import Scraper

courses = [
    'https://openclassrooms.com/fr/courses/2035736-mettez-en-place-lintegration-et-la-livraison-continues-avec-la-demarche-devops'
]

oc_scraper = Scraper()

for course in courses:
    oc_scraper.scrap_course(course)
