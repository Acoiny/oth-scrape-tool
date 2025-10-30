from urllib.request import urlopen
import csv
import datetime as dt

import requests

from bs4 import BeautifulSoup

class Meal:
    def __init__(self, name: str,
                 # kennzeichnung: str,
                 prices: list[str],
                 image_url: str) -> None:
        self.name = name
        # self.kennzeichnung = kennzeichnung
        self.price_students = prices[0].replace(',', '.')
        self.price_workers = prices[1].replace(',', '.')
        self.price_guest = prices[2].replace(',', '.')
        self.image_url = image_url
    def __str__(self) -> str:
        return f'{self.name} - : {self.price_students}'

    def to_markdown(self) -> str:
        image_format = f'<img src="{self.image_url}" width="200"/>'
        return f'|{image_format}|{self.name}|{self.price_students}|{self.price_workers}|{self.price_guest}|'

class Weekday:
    def __init__(self, datum: dt.date) -> None:
        # self.datum = dt.datetime.strptime(datum, "%d.%m.%Y").date()
        self.datum = datum.strftime('%d.%m.%Y')
        self.suppen: list[Meal] = []
        self.hauptspeisen: list[Meal] = []
        self.beilagen: list[Meal] = []
        self.nachspeisen: list[Meal] = []

    def add_meal(self, meal: Meal, meal_type: str) -> None:
        match meal_type.lower():
            case 'hauptgerichte':
                self.hauptspeisen.append(meal)
            case 'beilagen':
                self.beilagen.append(meal)
            case 'suppen':
                self.suppen.append(meal)
            case 'nachspeisen':
                self.nachspeisen.append(meal)
            case _:
                raise Exception(f'Unknown meal type: {meal_type}')

    def get_markdown_table_header(self) -> str:
        res  = '| Bilder | Name | Studentenpreis | Mitarbeiterpreis | Gästepreis |\n'
        res += '|--------|------|----------------|------------------|------------|\n'
        return res

    def to_markdown_str(self) -> str:
        res = '## Suppen\n'
        res += self.get_markdown_table_header()
        for su in self.suppen:
            res += f'{su.to_markdown()}\n'
        res += '## Beilagen\n'
        res += self.get_markdown_table_header()
        for vs in self.beilagen:
            res += f'{vs.to_markdown()}\n'
        res += '## Hauptspeisen\n'
        res += self.get_markdown_table_header()
        for hs in self.hauptspeisen:
            res += f'{hs.to_markdown()}\n'
        res += '## Nachspeisen\n'
        res += self.get_markdown_table_header()
        for ns in self.nachspeisen:
            res += f'{ns.to_markdown()}\n'

        return res

    def __str__(self) -> str:
        res = '    Suppen:\n'

        for su in self.suppen:
            res += f'       - {su}\n'
        res += '    Beilagen:\n'
        for vs in self.beilagen:
            res += f'       - {vs}\n'
        res += '    Hauptspeisen:\n'
        for hs in self.hauptspeisen:
            res += f'       - {hs}\n'
        res += '    Nachspeisen:\n'
        for ns in self.nachspeisen:
            res += f'       - {ns}\n'

        return res

class Mensaplan:
    """
    Gets the current mensaplan and handles stringifying it and
    formatting as markdown
    """
    def __init__(self, calendar_week: int | None = None, today: bool = False) -> None:

        # if no week is specified, use the current week
        if calendar_week == None:
            calendar_week = dt.datetime.today().isocalendar()[1]

        # we get a list of all dates and cache it
        self.weekdays = self.get_weekdays(calendar_week)

        # by default, we assume that we want to get all the days of the selected week
        self.dates: list[dt.date] = self.weekdays

        # if we only want today, we replace all days by the current date
        if today:
            self.dates = [ dt.datetime.today() ]

        self.url = 'https://stwno.de/infomax/daten-extern/html/speiseplan-render.php'
        self.days: dict[dt.date, Weekday] = {}

    def get_weekdays(self, week) -> list[dt.date]:
        """
        Returns all the dates of the current week
        """
        first_day_of_year = dt.date(dt.datetime.today().year, 1, 1)
        first_monday = first_day_of_year + dt.timedelta(weeks=week - 1, days=-first_day_of_year.weekday())
        # count from monday to friday
        weekdays = [first_monday + dt.timedelta(days=i) for i in range(5)]
        return weekdays

    def select_single_weekday(self, day: int) -> None:
        """
        Adds another day to request the mensaplan for
        """
        self.dates = [ self.weekdays[day] ]

    def get(self) -> None:
        """
        Fetches all the data for all added days
        """
        for day in self.dates:
            self.get_with_images(day)

    def get_with_images(self, date: dt.date) -> None:
        """
        Fetches the selected day's mensaplan with all it's images
        """
        data = {
                "date": date.strftime('%Y-%m-%d'),
                "func": "make_spl",
                "lang": "de",
                "locId": "HS-R-tag",
                "w": ""
        }

        # get the base url for images
        base_url: str = self.url[:self.url.rindex('/') + 1]

        res = requests.post(self.url, data=data).content
        soup = BeautifulSoup(res.decode('utf-8'), 'html.parser')
        headers = soup.find_all('tr')

        day = self.days.get(date)
        if day == None:
            day = Weekday(date)
            self.days[date] = day

        current_meal_type: str = ''

        for header in headers:
            cl = header.attrs.get('class')
            if not cl: continue

            if 'gruppenkopf' in cl:
                current_meal_type = header.find('td').get_text() # type: ignore
            if 'essenzeile' in cl:
                contents = header.find_all('td')
                preise: list = [ el.get_text() for el in header.find_all('td', class_='preis') ]
                name = contents[1].get_text()
                img_url: str = ''
                if img := contents[0].find('img'):
                    img_url = base_url + img['src'] # type: ignore
                day.add_meal(Meal(name, preise, img_url), current_meal_type)


    def to_markdown_str(self) -> str:
        res = ''
        weekdays = [
            'Montag',
            'Dienstag',
            'Mittwoch',
            'Donnerstag',
            'Freitag',
            'Samstag',
            'Sonntag'
        ]
        for d in self.days:
            day = self.days[d]
            try:
                res += f'# {weekdays[d.weekday()]} ({d.strftime("%d.%m.%Y")})\n'
                res += day.to_markdown_str() + '\n'
            except Exception as e:
                res += '> [!WARNING]\n> No mensaplan!\n'

        return res

    def __str__(self) -> str:
        res = ''
        weekdays = [
            'Montag',
            'Dienstag',
            'Mittwoch',
            'Donnerstag',
            'Freitag',
            'Samstag',
            'Sonntag'
        ]
        for day in self.days:
            res += f'{weekdays[day.weekday()]}:\n'
            res += str(self.days[day]) + '\n'
        return res

if __name__ == '__main__':
    m = Mensaplan(today=True)
    m.get()
    print(m)
