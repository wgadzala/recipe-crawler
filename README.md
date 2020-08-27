# Kwestia Smaku Crawler

This is a simple crawler designed to extract all cooking recipes from www.kwestiasmaku.com.

The project was shelved due to lack of access to a viable proxy list to implement proxy rotation.

## Description  

The crawler follows internal links to map the website and scrapes the pages containing recipes for the following:

- title,
- portions,
- ingredients,
- instructions,
- image,
- rating.

To avoid blocking the website content is requested via publicly available proxies (at random). In case of a rejected connection, the respective IP address is removed from the pool.

## Roadmap

Currently the scraping functions print out the results. If the project was not shelved a panda data frame / SQL database for storing results could be implemented. 

## License
[MIT](https://choosealicense.com/licenses/mit/)
