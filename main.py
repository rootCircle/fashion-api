from PIL import Image
import requests
import json

"""
API Calls based on https://rapidapi.com/DataCrawler/api/asos10/
"""

# Disable to have all sets of items
ENFORCE_API_LIMIT=True
MAX_API_CALLS=3
RAPID_API_KEY="b7e214e07cmsh48e876c8d143ab7p1650f8jsn9321a4c9ea75"

def main():
    items = get_items()
    
    categories = list(map(lambda x: x['title'], items))
    print("Categories : ", categories, "\n\n\n\n")

    menCategory = ["A-Z Men's Brands", "A-Z Men's Outlet Brands", 'Men']
    womenCategory = ["A-Z Women's Brands", 'Women']
    otherCategory = ['A-Z of brands: Outlet & sale']

    categoryMenIds = get_cat_id(items, menCategory)
    categoryWomenIds = get_cat_id(items, womenCategory)
    categoryOtherIds = get_cat_id(items, otherCategory)

    mens_products = []
    womens_products = []
    other_products = []

    counter=1

    # Half API calls reserved for mens
    for catId in categoryMenIds:
        counter+=1
        if ENFORCE_API_LIMIT and counter == MAX_API_CALLS // 3:
            break
        mens_products.extend(get_products(catId))

    # Other API calls for women
    for catId in categoryWomenIds:
        counter+=1
        if ENFORCE_API_LIMIT and counter == (MAX_API_CALLS * 2) // 3:
            break
        womens_products.extend(get_products(catId))

    for catId in categoryOtherIds:
        counter+=1
        if ENFORCE_API_LIMIT and counter == (MAX_API_CALLS * 2) // 3:
            break
        other_products.extend(get_products(catId))



    

    print("MENS : ", mens_products, "\n\n\n\n")
    print("WOMENS : ", womens_products, "\n\n\n\n")
    print("OTHER : ", other_products, "\n\n\n\n")



    # Sample Image 
    if len(mens_products) > 0:
        url_to_image("http://" + mens_products[0]['imageUrl']).show()

    if len(womens_products) > 0:
        url_to_image("http://" + womens_products[0]['imageUrl']).show()

    if len(other_products) > 0:
        url_to_image("http://" + other_products[0]['imageUrl']).show()


def get_products(catId):
    url = "https://asos10.p.rapidapi.com/api/v1/getProductList"

    querystring = {"categoryId":catId,"currency":"USD","country":"US","store":"US","languageShort":"en","sizeSchema":"US","limit":"200","offset":"0"}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "asos10.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    try:
        return response.json()["data"]["products"]
    except KeyError:
        print(response.json()["message"], "\n\n\n")
        return []

def get_cat_id(itemsAll, allowedCategory):
    categoryIds = set()
    for itemList in itemsAll:
        if itemList["title"] in allowedCategory:
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
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "asos10.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    try:
        data = data['data']

        category = []

        for key in data:
            for types in data[key]:
                category.append({"id": types['id'], "title": types['content']['title'], "children": types['children']})

        return category
    except KeyError:
        print(data["message"], "\n\n\n")
        return []


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