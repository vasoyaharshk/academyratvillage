import pandas as pd
import numpy as np
import os
import csv
from academy import time_utils
from user import settings


class Item(object):
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)


class Collection:
    def __init__(self, name, default_dict=None):
        self.items = []
        self.name = name
        self.path = os.path.join(settings.DATA_DIRECTORY, name + '.csv')
        self.read_from_csv(default_dict)

    def as_dict(self):
        my_dict = {}
        for k in self.items[0].__dict__.keys():
            my_dict[k] = list(np.concatenate(list([item.__dict__[k]] for item in self.items)))
        return my_dict

    def as_df(self):
        my_dict = self.as_dict()
        return pd.DataFrame(my_dict)

    def save_csv(self, date=None):
        if date:
            path = self.path[:-4] + date + '.csv'
        else:
            path = self.path
        my_df = self.as_df()
        my_df.to_csv(path, index=False, sep=';')

    def read_from_csv(self, default_dict):
        self.items = []
        try:
            my_df = pd.read_csv(self.path, sep=';')
            if default_dict is not None:
                for name in default_dict.keys():
                    if name not in list(my_df):
                        my_df[name] = np.nan
        except FileNotFoundError:
            new_dict = {'date': time_utils.now_string(), **default_dict, }
            my_df = pd.DataFrame(new_dict, index=[0])
            my_df.to_csv(self.path, index=False, sep=';')
        my_list_of_dicts = my_df.to_dict(orient='records')
        for my_dict in my_list_of_dicts:
            item = Item(my_dict)
            self.items.append(item)

    def add_new_item(self, item_dict, item=None):
        if item_dict.get('filename') == '':
            pass
        else:
            if self.items:
                if item is not None:
                    new_dict = item.__dict__.copy()
                    for key, value in item_dict.items():
                        new_dict[key] = value
                else:
                    new_dict = item_dict

                if 'date' in new_dict:
                    new_dict['date'] = time_utils.now_string()
                else:
                    new_dict = {'date': time_utils.now_string(), **new_dict}

                new_item = Item(new_dict)
                self.items.append(new_item)
                with open(self.path, 'a') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(new_item.__dict__.values())
                if len(self.items) > 100000:
                    old_items = self.items[:-50000]
                    new_items = self.items[-50000:]
                    last_date = '_' + old_items[-1].date[:10].replace('/', '')
                    self.items = old_items
                    self.save_csv(last_date)
                    self.items = new_items
                    self.save_csv()
            else:
                new_dict = {'date': time_utils.now_string(), **item_dict}
                new_item = Item(new_dict)
                self.items.append(new_item)
                self.save_csv()

    def read_first_value(self, column1, value):
        try:
            result = [item for item in self.items if item.__dict__[column1] == value][0]
        except (KeyError, IndexError):
            result = None
        return result

    def read_last_value(self, column1, value):
        try:
            result = [item for item in self.items if item.__dict__[column1] == value][-1]
        except (KeyError, IndexError):
            result = None
        return result

    def read_last_value_excluding(self, column1, value, column2, list_values_exclude):
        try:
            results = [item for item in self.items if item.__dict__[column1] == value]
            result = [item for item in results if item.__dict__[column2] not in list_values_exclude][-1]
        except (KeyError, IndexError):
            result = None
        return result

    def read_last_index(self, column1, value):
        try:
            result = [(index, item) for (index, item) in enumerate(self.items) if item.__dict__[column1] == value][-1]
            return result[0]
        except (KeyError, IndexError):
            return -1

    def read_last_index_excluding(self, column1, value, column2, list_values_exclude):
        try:
            results = [(index, item) for (index, item) in enumerate(self.items) if item.__dict__[column1] == value]
            result = [item for item in results if item[1].__dict__[column2] not in list_values_exclude][-1]
            return result[0]
        except (KeyError, IndexError):
            return -1
