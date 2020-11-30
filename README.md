# Hinzu <#-#>
---

The directory represents a project which has been started during [PhotoHack TikTok (March, 2019)](https://hacktiktok.photolab.me/). Since the event project evolve from tiny Flask app to the Django-backend and ReactApp-frontend as a one app with neural model for searching similar images through our parsed image db and other features, e.g. index search optimizations, calculation of offline, online metrics for analyzing and validation.

In two words, there are two apps:
1. Django app ([hinzu-django](https://hinzu.online/hinzu-django/)) with made frontended django views and the backend as it is.
2. The next one (frontend for the previous) is ReactApp ([hinzu.online](https://hinzu.online/)) which processing with backend Django side, i.e. django-rest-framework.

In addition, we save user appreciations as binary mark for resulted concated image ( user passed img with picked up similar image from film-image-base). So, we leave the possibility to improve our neural model.

## Briefly

> <i>Disclaimer</i>: this is not a well-written doc, thereby read on your own risk. Or merely check the bottom for creds.

- `django-app/`: web Hinzu as -//- app into 8000 port;
  - `web_app/`: django-app with few views & postgresql user rated data and made embeds;
    - `data/`: dir for data to match with. Should include following dirs as well:
      - `movies/`
      - `memes/`
      - `pinterest/`
      > this dirs should contain `embeds.npy` or `hnsw.zip` files and also `images/` dir with images accordingly;
  - `Dockerfile`: develop version of `web_app` uses `entrypoint.sh`;
  - `Dockerfile.prod`: production version uses `entrypoint.prod.sh`;

- `react-hinzu-app`: tiny front app. It uses django api-rest-framework. Nginx serves built files. So, after success `npm run build` and `scp -r build <server>:/home/ivan/`, change previous `build/` directory in a sec like following:
```
mv Hinzu/react-hinzu-app/build/ Hinzu/react-hinzu-app/last_build/ && mv build/ Hinzu/react-hinzu-app/build/ && rm -rf Hinzu/react-hinzu-app/last_build
```


- `docker-compose.yml`: develop version of app uses `.env.dev`;

- `docker-compose.prod.yml`: production version uses `.env.prod` & ``.env.prod.db``. To start type the following
```
docker-compose -f docker-compose.prod.yml up
```
If want also build image and run just diemon use flags `--build` and `-d` accordingly. To see logs after used diemon flag type `logs -f`:
```
docker-compose -f docker-compose.prod.yml logs -f
```

- `hinzu_project`: conf file from hinzu dev. server with nginx settings, should be located in `/etc/nginx/sites-available/`. To activate this configuration dnf to pass those settings to `sites-enable/` dir:
```
sudo ln -s /etc/nginx/sites-available/hinzu_project /etc/nginx/sites-enabled
```

- `search/`: scripts for making embeds & hnsw and other investigating/searching staff;

- `SCRAPPER/`: additional code of imgs scrapping (Selenium and BeautifulSoup);

## Tips & tricks
- Where is reports&logs when it is prod version is running: all in volume and can be founded into mounted dirs on host. How to find:
```
docker volume ls
docker volume inspect <volume name>
```

### What templates for similar images are used there?
All magic happens according to `django-app/web_app/script.py` file. There is ImageTemplate class with a few methods:
- `to_movie` : this template runs on server,
- `to_blurface` : just available template with 2 backgrounds.

## Credential (c)

The Team:
- [Olga](https://github.com/OlgaRemit)
- [Serg](https://github.com/sergmiller)
- [Ivan](https://github.com/AlcibiadesCleinias)
- [Tim](https://github.com/toren332)
