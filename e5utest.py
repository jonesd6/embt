import csv
import requests
import numpy as np
import time
import random
import datetime
import matplotlib.pyplot as plt
from operator import itemgetter
import pandas as pd

def get_data_from_csv(filename):
    raw_data = pd.read_csv(filename, 
                            delimiter=',',
                            header=0,
                            index_col=0)
    return raw_data


file_price_history = 'mock.csv.csv'
  
price_history = get_data_from_csv(file_price_history)


print(price_history)