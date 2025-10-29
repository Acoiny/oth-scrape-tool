import requests

from bs4 import BeautifulSoup

# TODO: finish parsing mensaplan and sort images to their corresponding entry
# this will replace using the csv

def get_image_urls(baseUrl: str, date) -> list[str]:
    res = requests.post("https://stwno.de/infomax/daten-extern/html/speiseplan-render.php", data={"date": "2025-10-29", "func": "make_spl", "lang": "de", "locId": "HS-R-tag", "w": ""}).content

    soup = BeautifulSoup(res.decode('utf-8'), 'html.parser')
    #imgs = soup.find_all('img')
    meals = soup.find_all('tr')
    for meal in meals:
        print('-'*50)
        print(dir(meal['class'])) # type: ignore
        print('-'*50)

    return []

    urls: list[str] = []

    for img in imgs:
        if "Bilder" in img['src']:  # type: ignore
            urls.append(img['src']) # type: ignore

    return urls

urls = get_image_urls("asd", "")

print(urls)
