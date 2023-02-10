import requests
from bs4 import BeautifulSoup
import re


class GamesParser:
    def __init__(self, url, menu_endpoints, items):
        self.url = url
        self.menu_endpoints = menu_endpoints
        self.items = items

    def parse_games_data(self):

        for link in self._get_links_upcoming_games_by_item():
            page = requests.get(url=link)

            soup_game = BeautifulSoup(page.content, "html.parser")

            game_name = soup_game.find('span', attrs={'id': 'game-title-cnt'}).text

            game_publisher = soup_game.\
                find('span', attrs={'id': 'game-publisher-cnt'}).\
                find('a', class_='un-link').text

            game_developer = soup_game. \
                find('span', attrs={'id': 'game-developer-cnt'}). \
                find('a', class_='un-link').text

            try:
                game_release_date_day = soup_game.find('p', class_='p2 data-before').\
                    find('span', class_='s1').text
            except AttributeError:
                game_release_date_day = ''
            try:
                game_release_date_month = soup_game.\
                    find('p', class_='p2 data-before').find('span', class_='s2').text
            except AttributeError:
                game_release_date_month = ''
            try:
                game_release_date_year = soup_game.find('p', class_='p2 data-before').\
                    find('span', class_='s3').text
            except AttributeError:
                game_release_date_year = ''
            game_release_date = game_release_date_day + game_release_date_month + game_release_date_year

            try:
                game_platforms = [platform.text for platform in soup_game.find('div', class_='multi-p').find_all('a')]
            except AttributeError:
                game_platforms = ''

            game_genres = [genre.text for genre in soup_game.find('span', attrs={'id': 'game-genre-cnt'}).find_all('a')]

            game_description = soup_game.find('div', attrs={'id': 'game-description-cnt'}).find('p').text

            game_screenshots = str(soup_game.select('body > main > section > article > header > div.S016-guz-mid-c > div > a:nth-child(2)'))
            try:
                game_screenshots = re.search(r'href=\"(.*?)\">Images', game_screenshots).group(1)
            except AttributeError:
                game_screenshots = ''

            game_trailer = str(soup_game.select('body > main > section > article > header > div.S016-guz-mid-c > div > a:nth-child(3)'))
            try:
                game_trailer = re.search(r'href=\"(.*?)\">Video', str(game_trailer)).group(1)
            except AttributeError:
                game_trailer = ''

            yield {'game_name': game_name, 'game_publisher': game_publisher,
                   'game_developer': game_developer, 'game_release_date': game_release_date,
                   'game_platforms': game_platforms, 'game_genres': game_genres,
                   'game_description': game_description, 'game_screenshots': game_screenshots,
                   'game_trailer': game_trailer, 'source_link': link}

    def _get_links_upcoming_games_by_item(self):
        upcoming_games_links = []
        for developer in self._developers_pages():
            page = requests.get(url=developer[0])

            soup_menu = BeautifulSoup(page.content, "html.parser")
            developer_page = soup_menu.select('body > main > section > div:nth-child(7) > div > div.dev-right > p')
            for game in developer_page:
                upcoming_games_links.append(self.url + game.find("a")['href'][1:])

        return upcoming_games_links

    def _create_alphabet_menu(self):
        pages_urls = []
        for menu_endpoint in self.menu_endpoints:
            pages_urls.append(dict())

        for index, endpoint in enumerate(self.menu_endpoints):
            page = requests.get(url=self.url + endpoint)

            soup_menu = BeautifulSoup(page.content, "html.parser")

            buttons = soup_menu.find("div", class_="buttons")
            buttons_list = buttons.find_all("a", class_="but-neu")

            for button in buttons_list:
                pages_urls[index][button.text.lower()] = self.url + button['href']

        return pages_urls

    def _developers_pages(self):
        result = []
        checked_items = []
        for letter_item in self._letters_pages():
            page = requests.get(url=letter_item[0])

            soup_menu = BeautifulSoup(page.content, "html.parser")

            lista = soup_menu.find("div", class_="lista")
            lista_item = lista.find_all("a")

            for list_item in lista_item:
                if letter_item[1].lower() in list_item.text.lower()\
                        and letter_item[1].lower() not in checked_items:
                    result.append((self.url + list_item['href'], letter_item[1]))
                    checked_items.append(letter_item[1].lower())
        return result

    def _letters_pages(self):
        alphabet_menu = self._create_alphabet_menu()
        result = []
        for menu in alphabet_menu:
            for item in self.items:
                try:
                    int(item[0])
                    first_symbol = '0-9'
                except ValueError:
                    first_symbol = item[0].lower()
                if item not in result:
                    result.append((str(menu[first_symbol]), item))
        return result


if __name__ == '__main__':
    url = 'https://www.gamepressure.com/'
    endpoints = ['/games/game-companies.asp?GRU=2', '/games/game-companies.asp?GRU=1']

    items_list = [
        '2K', 'Remedy', 'Ubisoft',
        'Infinity Ward', 'Annapurna Interactive', 'Electronic Arts',
        'Zynga', 'People Can Fly', 'Square Enix',
        'Activision'
    ]
    parser = GamesParser(url=url, menu_endpoints=endpoints, items=items_list)

    games_data = parser.parse_games_data()
    for game in games_data:
        print(game)
