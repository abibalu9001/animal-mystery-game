import requests


def get_wikipedia_image(animal_name):

    url = "https://en.wikipedia.org/w/api.php"

    params = {

        "action": "query",

        "titles": animal_name,

        "prop": "pageimages",

        "format": "json",

        "pithumbsize": 800

    }

    headers = {

        "User-Agent":
        "AnimalMysteryBot/1.0"

    }

    response = requests.get(

        url,

        params=params,

        headers=headers,

        timeout=10

    )

    # DEBUG
    print(response.status_code)

    data = response.json()

    pages = data["query"]["pages"]

    for page_id in pages:

        page = pages[page_id]

        if "thumbnail" in page:

            return page["thumbnail"]["source"]

    return None


animal = "lion"

image_url = get_wikipedia_image(animal)

print(image_url)
