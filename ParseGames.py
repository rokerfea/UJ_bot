import requests
from bs4 import BeautifulSoup

class Games_parse:
    def __init__(self):
        self.url = 'https://yandex.ru/games/'
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, 'lxml')
        self.names = self.soup.find_all('span', class_='game-card__title')
        self.authors = self.soup.find_all('span', class_='game-card__developer')
        self.ratings = self.soup.find_all('span', class_='popularity-badge__rating')
        self.images = self.soup.find_all('img', class_='game-image game-image_size_size36 game-image_mode_online game-card__game-icon')

    def games(self):
        self.games = []
        for name, author, rating, image in zip(self.names, self.authors, self.ratings, self.images):
            time_dict = {}
            time_dict["name"] = name.text
            time_dict["author"] = author.text
            time_dict["rating"] = rating.text
            time_dict["image"] = image.get('src')
            self.games.append(time_dict)
            if len(self.games) >= 10:
                return(self.games)
        return(self.games)


# Games_parse().games()
