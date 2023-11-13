from dotenv import dotenv_values
from pymongo import MongoClient
import pandas as pd
import datetime

config = dotenv_values(".env")


def handle_quality(row_value: str):
    if row_value.find('1a'):
        return 'Primera'
    if row_value.find('2a'):
        return 'Segunda'


def begin(data_route, delimiter='|'):
    client = MongoClient(config["ADRESS"], 27017)
    db = client[config["DB_NAME"]]

    data = pd.read_csv(data_route, delimiter=delimiter)
    data = data.iloc[::-1]
    print(data.head(10))
    # data.fillna('Sin especificar')
    print(data.info())
    for col in data:
        print(data[col].name)
        print(data[col].unique())
        print(len(data[col].unique()))

    data_no_duplicates = data.drop_duplicates(subset='Producto', keep="first")
    print(data_no_duplicates["Producto"])
    for i, row in data_no_duplicates.iterrows():
        db['foods'].insert_one({
            'product_name': row['Producto'],
            'group': row['Grupo']
        })

    curr_idx = 0
    data_len = len(data.index)
    for i, row in data.iterrows():
        food_doc = db['foods'].find_one({'product_name': row['Producto']})
        db['history'].insert_one({
            'date': datetime.datetime.strptime(str(row['Fecha']), '%d/%m/%Y %H:%M:%S'),
            'region': row['Region'],
            'sector': row['Sector'],
            'point_type': row['Tipo_de_punto'],
            'variety': row['Variedad'],
            'quality': handle_quality(row['Calidad']),
            'unit': row['Unidad'],
            'min_price': row['PrecioMinimo'],
            'mean_price': float(str(row['PrecioPromedio']).replace(',', '.')),
            'max_price': row['PrecioMaximo'],
            'food_id': food_doc.get('_id')
        })
        curr_idx += 1
        print(f'{curr_idx} row/s out of {data_len}')


if __name__ == '__main__':
    user_input = input("Insert route: ")
    if user_input.endswith((".csv", ".tsv")):
        begin(user_input, delimiter='|')
    else:
        print('error')
