import requests
import re
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from movies.models import Movie
import time
import json

class Command(BaseCommand):
    help = 'Scrape top 5000 movies from the given HTML page and store in DB'

    def handle(self, *args, **options):
        url = "https://dls2.iran-gamecenter-host.com/DonyayeSerial/top_5000_movies.html"
        self.stdout.write(f"Fetching {url} ...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            self.stderr.write(f"Error fetching page: {e}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        # جدا کردن فیلم‌ها بر اساس تگ <hr>
        # هر فیلم با <hr> شروع می‌شود (قسمت بالا یک هدر دارد که باید رد شود)
        # ابتدا تمام <hr> ها را پیدا می‌کنیم، سپس هر بخش را تجزیه می‌کنیم.
        hr_tags = soup.find_all('hr')
        film_count = 0
        for hr in hr_tags[:-1]:  # آخری را نادیده بگیر
            # هر بخش فیلم بین این hr و hr بعدی است
            content = []
            for sibling in hr.next_siblings:
                if sibling.name == 'hr':
                    break
                if sibling.name is not None:
                    content.append(sibling)
            # تجزیه محتوای این بخش
            film_data = self.parse_film_section(content)
            if film_data:
                # ذخیره یا به‌روزرسانی
                obj, created = Movie.objects.update_or_create(
                    imdb_code=film_data['imdb_code'],
                    defaults={
                        'title': film_data['title'],
                        'year': film_data['year'],
                        'imdb_votes': film_data['imdb_votes'],
                        'imdb_rate': film_data['imdb_rate'],
                        'download_links': film_data['download_links']
                    }
                )
                if created:
                    film_count += 1
                    self.stdout.write(f"Added: {obj.title}")
                # تأخیر کم جهت جلوگیری از فشار
                time.sleep(0.01)
        self.stdout.write(f"Total new movies added: {film_count}")

    def parse_film_section(self, content):
        # پیدا کردن تگ h3 برای عنوان
        title_h3 = None
        for tag in content:
            if tag.name == 'h3':
                title_h3 = tag
                break
        if not title_h3:
            return None
        title_text = title_h3.get_text(strip=True)
        # title pattern: "1. The Shawshank Redemption 1994"
        match = re.match(r'\d+\.\s*(.+)\s+(\d{4})$', title_text)
        if not match:
            return None
        title = match.group(1).strip()
        year = int(match.group(2))

        # سپس سایر پاراگراف‌ها را می‌خوانیم
        imdb_code = None
        imdb_votes = None
        imdb_rate = None
        download_links = {"SoftSub": [], "Dubbed": []}
        section_type = None  # 'SoftSub' یا 'Dubbed'

        for tag in content:
            if tag.name == 'p':
                texts = tag.stripped_strings
                full_text = ' '.join(texts)
                if 'IMDb Code:' in full_text:
                    # استخراج کد
                    code_match = re.search(r'IMDb Code:\s*(\w+)', full_text)
                    if code_match:
                        imdb_code = code_match.group(1)
                elif 'IMDb Votes:' in full_text:
                    # "IMDb Votes: 3,152,101"
                    votes_match = re.search(r'IMDb Votes:\s*([\d,]+)', full_text)
                    if votes_match:
                        imdb_votes = votes_match.group(1).replace(',', '')
                elif 'IMDb Rates:' in full_text:
                    rate_match = re.search(r'IMDb Rates:\s*([\d.]+)', full_text)
                    if rate_match:
                        imdb_rate = float(rate_match.group(1))
                elif 'SoftSub' in full_text and 'color:#ff0000' in str(tag):
                    section_type = 'SoftSub'
                elif 'Dubbed' in full_text and 'color:#339966' in str(tag):
                    section_type = 'Dubbed'
                else:
                    # احتمالاً لینک دانلود است
                    if section_type and tag.find('a'):
                        for a_tag in tag.find_all('a'):
                            href = a_tag.get('href')
                            link_text = a_tag.get_text(strip=True)
                            # معمولاً متن شامل کیفیت و بعد / حجم است
                            if href and 'http' in href:
                                # حجم معمولاً بعد از لینک می‌آید
                                size_text = tag.get_text()
                                size_match = re.search(r'/\s*([\d.]+\s*(GB|MB))', size_text, re.IGNORECASE)
                                size = size_match.group(0).replace('/', '').strip() if size_match else ''
                                download_links[section_type].append({
                                    'quality': link_text,
                                    'url': href,
                                    'size': size
                                })

        if not imdb_code:
            return None

        return {
            'title': title,
            'year': year,
            'imdb_code': imdb_code,
            'imdb_votes': imdb_votes,
            'imdb_rate': imdb_rate,
            'download_links': download_links
        }