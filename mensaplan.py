from urllib.request import urlopen
import csv
import datetime as dt

import requests

from bs4 import BeautifulSoup

class Meal:
    def __init__(self, name: str,
                 kennzeichnung: str,
                 price_students: str,
                 price_workers: str,
                 price_guest: str,
                 image_url: str) -> None:
        self.name = name
        self.kennzeichnung = kennzeichnung
        self.price_students = float(price_students.replace(',', '.'))
        self.price_workers = float(price_workers.replace(',', '.'))
        self.price_guest = float(price_guest.replace(',', '.'))
        self.image_url = image_url
    def __str__(self) -> str:
        return f'{self.name} - {self.kennzeichnung}: {self.price_students:.2f}€'

class Weekday:
    def __init__(self, datum: str) -> None:
        self.datum = dt.datetime.strptime(datum, "%d.%m.%Y").date()
        self.suppen: list[Meal] = []
        self.hauptspeisen: list[Meal] = []
        self.beilagen: list[Meal] = []
        self.nachspeisen: list[Meal] = []

    def add_meal(self, meal: Meal, meal_type: str) -> None:
        if meal_type.startswith('HG'):
            self.hauptspeisen.append(meal)
        elif meal_type.startswith('B'):
            self.beilagen.append(meal)
        elif meal_type.startswith('Suppe'):
            self.suppen.append(meal)
        elif meal_type.startswith('N'):
            self.nachspeisen.append(meal)
        else:
            raise Exception(f'Unknown meal type: {meal_type}')

    def to_markdown_str(self) -> str:
        res = '## Suppen\n'
        for su in self.suppen:
            res += f'- {su}\n'
        res += '## Beilagen\n'
        for vs in self.beilagen:
            res += f'- {vs}\n'
        res += '## Hauptspeisen\n'
        for hs in self.hauptspeisen:
            res += f'- {hs}\n'
        res += '## Nachspeisen\n'
        for ns in self.nachspeisen:
            res += f'- {ns}\n'

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
    def __init__(self, calendar_week: int | None, today: bool) -> None:
        # always use the current week if today is set
        # if it is not set, then allow a custom calendar week
        if today or calendar_week == None: calendar_week = dt.date.today().isocalendar()[1]
        self.today = today
        self.url = f'https://www.stwno.de/infomax/daten-extern/csv/HS-R-tag/{calendar_week}.csv'
        self.url_images = f'https://stwno.de/infomax/daten-extern/html/speiseplan-render.php'
        self.days: dict[str, Weekday] = {}

    def get(self) -> None:
        """
        Fetches the current mensaplan and stores it
        """
        with urlopen(self.url) as url:
            lines = [l.decode('latin-1').strip() for l in url.readlines()]
            csv_reader = csv.reader(lines, delimiter=';')

            # discard fields
            next(csv_reader)

            for row in csv_reader:
                day = self.days.get(row[1])
                if day == None:
                    day = Weekday(row[0])
                    self.days[row[1]] = day
                meal = Meal(row[3], row[4], row[6], row[7], row[8]) # pyright: ignore
                day.add_meal(meal, row[2])

    def get_with_images(self) -> None:
        """
        Fetches the current mensaplan with all it's images
        """
        data = {
                "date": ASDAS,
                "func": "make_spl",
                "lang": "de",
                "locId": "HS-R-tag",
                "w": ""
        }

        res = requests.post("https://stwno.de/infomax/daten-extern/html/speiseplan-render.php", data=data)


    def to_markdown_str(self) -> str:
        res = ''

        keys_to_names = [
            ('Mo', 'Montag'),
            ('Di', 'Dienstag'),
            ('Mi', 'Mittwoch'),
            ('Do', 'Donnerstag'),
            ('Fr', 'Freitag'),
            ('Sa', 'Samstag'),
            ('So', 'Sonntag')
        ]

        if self.today:
            index = dt.date.today().isocalendar()[2] - 1
            key, name = keys_to_names[index]
            res += f'# {name}\n'

            day = self.days.get(key, None)

            if day == None: res += 'No mensaplan for today!\n'
            else: res += f'{day.to_markdown_str()}'
        else:
            for key, name in keys_to_names[:-2]:
                try:
                    res += f'# {name}\n'
                    res += f'{self.days[key].to_markdown_str()}'
                except:
                    res += f'> [!WARNING]\n> No mensaplan!\n'

        return res

    def stringify_day(self, index: int) -> str:
        keys_to_names = [
            ('Mo', 'Montag'),
            ('Di', 'Dienstag'),
            ('Mi', 'Mittwoch'),
            ('Do', 'Donnerstag'),
            ('Fr', 'Freitag'),
            ('Sa', 'Samstag'),
            ('So', 'Sonntag')
        ]

        try:
            return f'{keys_to_names[index][1]}:\n{self.days[keys_to_names[index][0]]}\n'
        except:
            return f'No mensaplan for {keys_to_names[index][1]}\n'

    def __str__(self) -> str:
        res = ''

        if self.today:
            index = dt.date.today().isocalendar()[2] - 1
            res += self.stringify_day(index)
        else:
            for i in range(5):
                res += self.stringify_day(i)

        return res

if __name__ == '__main__':
    m = Mensaplan(None, False)
    m.get()
    print(m)
