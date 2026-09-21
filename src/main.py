import pandas as pd
import numpy as np

books = pd.read_csv('D:\\Python\\DE5\\DE5M5.2\\data\\raw\\library.csv')
customers = pd.read_csv('D:\\Python\\DE5\\DE5M5.2\\data\\raw\\library_customers.csv')

print(books.head())
print(customers.head())

books.shape # Number of rows and columns in the books DataFrame
books.isnull().all().sum()  # Number of columns in the books DataFrame that contain only null values
# real = books.dropna(how='all')  # Drop rows where all elements are NaN

# print(real.shape)
# print(real.head())

# Convert the 'Book checkout' and 'Book return' columns to datetime format
# 
checkout_cleaned = books['Book checkout'].astype('string').str.replace('"', '', regex=False).str.strip()
parsed_checkout = pd.to_datetime(checkout_cleaned, format='%d/%m/%Y', errors='coerce')
books['Book checkout'] = parsed_checkout
return_cleaned = books['Book Returned'].astype('string').str.replace('"', '', regex=False).str.strip()
parsed_return = pd.to_datetime(return_cleaned, format='%d/%m/%Y', errors='coerce')
books['Book Returned'] = parsed_return

# print(books.head())

print(books.duplicated())