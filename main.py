from PIL import Image
import requests
import json

"""
API Calls based on https://rapidapi.com/DataCrawler/api/asos10/
"""

ENFORCE_API_LIMIT=True
MAX_API_CALLS=3

def main():
    items = get_items()
    
    categories = list(map(lambda x: x['title'], items))
    print("Categories : ", categories, "\n\n\n\n")

    categoryIds = get_cat_id(items)


    products = []
    
    counter=1
    for catId in categoryIds:
        counter+=1
        if ENFORCE_API_LIMIT and counter == MAX_API_CALLS:
            break
        products.extend(get_products(catId))

    print(products)
    

    # Sample Image showing
    url_to_image("http://" + products[0]['imageUrl']).show()

def get_products(catId):
    url = "https://asos10.p.rapidapi.com/api/v1/getProductList"

    querystring = {"categoryId":catId,"currency":"USD","country":"US","store":"US","languageShort":"en","sizeSchema":"US","limit":"200","offset":"0"}

    headers = {
        "X-RapidAPI-Key": "a71549cbabmsh2e17a51866bd59bp1f181djsn1042c51dc488",
        "X-RapidAPI-Host": "asos10.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()["data"]["products"]

def get_cat_id(itemsAll):
    categoryIds = set()
    for itemList in itemsAll:
        for item in itemList["children"]:
            catId = item["link"]
            if catId is not None:
                categoryIds.add(catId["categoryId"])

    return categoryIds

def get_items():
    """
    Returns a list of objects with members id, title(group name) 
    and list of products in that category
    """

    url = "https://asos10.p.rapidapi.com/api/v1/getCategories"

    headers = {
        "X-RapidAPI-Key": "a71549cbabmsh2e17a51866bd59bp1f181djsn1042c51dc488",
        "X-RapidAPI-Host": "asos10.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    data = response.json()['data']

    category = []

    for key in data:
        for types in data[key]:
            category.append({"id": types['id'], "title": types['content']['title'], "children": types['children']})

    return category


def url_to_image(url):
    try:
        response = requests.get(url, stream=True)

        if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
            pil_image = Image.open(response.raw)
            return pil_image
        else:
            print("Image can't be retrieved!")
            return False

    except Exception as e:
        print(e)


if __name__ == '__main__': 
    main()