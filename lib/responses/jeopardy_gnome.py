import requests
import json
import math

# A Gnome that mines for jeopardy clues
ENDPOINT = "http://jservice.io/api/"

def get_n_categories(n):
  categories = []
  offset = 0
  count = 0
  print('Getting category list..')
  for index in range(0,math.ceil(n/100)):
    if n % 100 and count == 0:
      count = n  % 100
    else:
      count = 100 
    print('Getting {} categories!'.format(count))
    print('Has: {}, Goal: {}, {}%'.format(offset,n,offset/n*100))
    page = requests.get(ENDPOINT + 'categories?count={}&offset={}'.format(count,offset))
    print('Categories: {} to {}'.format(offset,offset + count))
    print(page.json())
    categories = categories + page.json()
    offset += count
  print('Getting full categories..')
  full_categories = []
  for index,category in enumerate(categories):
    print('Getting category: {}'.format(category['title']))
    print('{} of {} {}%'.format(index + 1,len(categories),index/len(categories)*100))
    full_categories += [get_full_category(category['id'])]

  return full_categories

def get_full_category(category_id):
  return requests.get(ENDPOINT + 'category?id={}'.format(category_id)).json()

categories = get_n_categories(10000)

print(len(categories))

print('Dumping data')
with open('questions.json','w') as outfile:
  json.dump(categories, outfile)



