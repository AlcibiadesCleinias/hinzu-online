import requests
from bs4 import BeautifulSoup
import urllib.request


for i in range(1, 21):
    html = requests.get(f'https://imgflip.com/memetemplates?page={i}').text
    soup = BeautifulSoup(html, 'html.parser')
    mydiv = soup.findAll("div", {"class": "mt-boxes"})
    images = soup.findAll("img")
    for image_tag in images[1:]:
        img_url = 'https://'+image_tag.get('src')[2:]
        img_name = img_url.split('/')[-1]
        img_data = requests.get(img_url).content
        with open('images/'+img_name, 'wb') as handler:
            handler.write(img_data)



