from logging import raiseExceptions
import random
import datetime
import calendar
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
import json


class SynthRetailOrders():

  #-----------------------------------------------------
  # Constants

  DC_CARRIERS:list = ["UPS", "FedEx", "USPS"]


  DC_NODES: list = ["Austin", "Dallas", "Houston"]


  MT_SKUS = pd.read_csv('config/mt_references - mt_skus.csv').set_index('sku')
  MT_NODES = pd.read_csv('config/mt_references - mt_nodes.csv').set_index('id')
  MT_CUSTOMERS = pd.read_csv('config/mt_references - mt_customers.csv').set_index('id')


  MT_SKUS['price'] = MT_SKUS['price'].astype(float)
  MT_NODES_DC = MT_NODES[MT_NODES['type'] == 'dc']
  MT_NODES_STORE = MT_NODES[MT_NODES['type'] == 'store']

  def __init__ (self,
                order_count=1000,
                customer_count=50,
                sku_count=100,
                catalog=None,
                store_ratio=0.6,
                start_date=datetime.date(2023,1,1),
                end_date=datetime.date(2023,12,31),
                curve="normal",
                format="JSON",
                **kwargs
              ):

  # default all input parameters if not furnished
    self.order_count = order_count
    self.customer_count = customer_count
    self.sku_count = sku_count
    self.catalog = catalog
    self.startDate = start_date
    self.endDate = end_date
    self.curve = curve
    self.format = format
    self.store_ratio = store_ratio

    # initialize other common variables
    self.distribution = None
    self.orders_by_day = None
    self.selected_ids = None
    self.sku_ids = None
    self.today = None
    self.order:dict = {}
    self.ol:dict = {}

    self.total_days:int = (self.endDate - self.startDate).days
    if self.total_days <= 0:
      self.total_days = 365

    # randomly pick master table data; customer, node, sku
    self.custList: list = random.sample(self.MT_CUSTOMERS.index.tolist(),
                                  self.customer_count)


    self.skuList: list = random.sample(self.MT_SKUS.index.tolist(),
                                  sku_count)


  #-----------------------------------------------------
  # determines the curve to spread the orders across date range

  def _orderSpread(self, num_orders, num_days, curve):
    orders_per_day = np.zeros(num_days)
    if curve == 'normal':
      distribution = np.random.normal(loc=num_days/2, scale=num_days/6, size=num_orders)
    elif curve == 'uniform':
      distribution = np.random.uniform(low=1, high=num_days, size=num_orders)
    elif curve == 'poisson':
      distribution = np.random.poisson(lam=num_orders/num_days, size=num_orders)
    else:
      raise ValueError("Invalid curve type. Must be one of 'normal', 'uniform', or 'poisson'.")

    days = np.clip(np.round(distribution),0,num_days-1).astype(int)
    orders_per_day = np.bincount(days, minlength=num_days)
    return(orders_per_day)

    #---------------------------------------------------


  def _genOrder(self,today, startDate)->dict:

    order: dict = {}
    order_no = f'O-{random.randint(10000000,99999999)}'
    order['order_no'] = order_no
    order['order_date'] = (startDate + datetime.timedelta(days=today)).isoformat()
    customer_no = (random.choice(random.sample(self.MT_CUSTOMERS.index.tolist(),self.customer_count)))
    order['customer'] = customer_no


    channel = random.choices(['Web','Store'],weights=[1.0-self.store_ratio, self.store_ratio])[0]

    if (channel == 'Web'):
      node = random.choice(self.MT_NODES_DC.index.tolist())
      method = random.choice(self.DC_CARRIERS)
      region = ''
      format = ''
    elif (channel == 'Store'):
      node = random.choice(self.MT_NODES_STORE.index.tolist())
      method = f'POS-{today}-{random.randint(1,10)}'
      region = self.MT_NODES_STORE.loc[node, 'region']
      format = self.MT_NODES_STORE.loc[node, 'format']
    else:
      print('NONE')

    order['channel'] = channel
    order['node'] = node
    order['method'] = method
    order['region'] = region
    order['format'] = format

    order_lines: list = []


    single_line: dict = {}
    #single_line['order_no'] = order_no
    nbr_of_lines = random.randint(1,5)

    for oline in range(nbr_of_lines):
      single_line['line'] = oline+1
      sku = random.choice(self.MT_SKUS.index.tolist())
      price:float = round(self.MT_SKUS.loc[sku,'price'],2)
      dept = self.MT_SKUS.loc[sku,'dept']
      quantity:int = round(random.randint(1,5))
      amount:float = round(price * quantity,2)
      single_line['sku'] = sku
      single_line['dept'] = dept
      single_line['quantity'] = quantity
      single_line['price'] = price
      single_line['amount'] = amount
      order_lines.append(single_line.copy())

    order['ol'] = order_lines
    return(order)


  # ___ [ PUBLIC METHODS ] ___

  def generateTx(self,**kwargs):
    self.transactions:list = []
    if 'order_count' in kwargs:
      self.order_count = kwargs['order_count']

    orders_by_day: list = self._orderSpread(num_orders=self.order_count,
                              num_days=self.total_days,
                              curve=self.curve)

    # for each day within the range,loop
    for today in range(self.total_days):
      todays_date = self.startDate + datetime.timedelta(days=today)
      order_no = random.randint(10000000,99999999)
      order_date = self.startDate + datetime.timedelta(days=today) # loop thru orders for day

      # for all the orders to be generated for the day
      for order_count in range(orders_by_day[today]):
        order = self._genOrder(today, startDate=self.startDate)
        self.transactions.append(order)



    return(self.transactions)

  def plotDistribution(self):
    # 1. Order Volume Distribution
    # Convert transactions to DataFrame for easier analysis
    df = pd.DataFrame(self.transactions)

    # Extract order date and total order value
    df['order_date'] = pd.to_datetime(df['order_date']).dt.date
    df['total_order_value'] = df['ol'].apply(lambda x: sum(item['amount'] for item in x))

    # Group by order date and calculate order count and total order value
    order_volume = df.groupby('order_date').agg(order_count=('order_no', 'count'), total_order_value=('total_order_value', 'sum'))

    # Plot order count and total order value over time
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(order_volume.index, order_volume['order_count'], color='blue', label='Order Count')
    ax1.set_xlabel('Order Date')
    ax1.set_ylabel('Order Count', color='blue')
    ax1.tick_params('y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(order_volume.index, order_volume['total_order_value'], color='red', label='Total Order Value')
    ax2.set_ylabel('Total Order Value', color='red')
    ax2.tick_params('y', labelcolor='red')

    plt.title('Order Volume Distribution')
    plt.legend()
    plt.show()

    # 2. Selected Customer Order Distribution
    selected_customers = random.sample(self.custList, 5)  # Select 5 random customers
    selected_customer_data = df[df['customer'].isin(selected_customers)]  # Filter data for selected customers
    selected_customer_distribution = selected_customer_data.groupby('customer')['order_no'].count().reset_index()
    selected_customer_distribution = selected_customer_distribution.rename(columns={'order_no': 'order_count'})

    plt.figure(figsize=(10, 6))
    plt.bar(selected_customer_distribution['customer'], selected_customer_distribution['order_count'])
    plt.xlabel('Customer')
    plt.ylabel('Order Count')
    plt.title('Order Distribution for Selected Customers (Bar Chart)')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.show()

    # 3. SKU Distribution
    sku_distribution = df.explode('ol').groupby(['order_date', 'ol'])['ol'].count().reset_index(name='count')
    sku_distribution = sku_distribution.merge(pd.DataFrame(df['ol'].tolist()[0]), on='ol', how='left')  # Assuming all 'ol' lists have the same structure
    plt.figure(figsize=(12, 6))
    plt.scatter(sku_distribution['order_date'], sku_distribution['sku'], s=sku_distribution['count'] * 10, alpha=0.5)
    plt.xlabel('Order Date')
    plt.ylabel('SKU')
    plt.title('SKU Distribution')
    plt.show()

    # 4. Node Distribution
    node_distribution = df.groupby(['order_date', 'fulfill_node'])['order_no'].count().reset_index()
    plt.figure(figsize=(12, 6))
    plt.scatter(node_distribution['order_date'], node_distribution['fulfill_node'], s=node_distribution['order_no'] * 10, alpha=0.5)
    plt.xlabel('Order Date')
    plt.ylabel('Fulfillment Node')
    plt.title('Node Distribution')
    plt.show()

    # 5. Channel Distribution
    channel_distribution = df.groupby(['order_date', 'channel'])['order_no'].count().reset_index()
    plt.figure(figsize=(12, 6))
    plt.bar(channel_distribution['order_date'], channel_distribution['order_no'], color=['blue' if c == 'Web' else 'red' for c in channel_distribution['channel']])
    plt.xlabel('Order Date')
    plt.ylabel('Order Count')
    plt.title('Channel Distribution')
    plt.legend(['Web', 'Store'])  # Assuming 'node' represents Store channel
    plt.show()
    return

def main():
  OUTPUT = '/content/drive/MyDrive/1Colab/synthcurve/output/transactions.json'

  transactions = SynthRetailOrders(customer_count=25)
  tx = transactions.generateTx(order_count=10000)
  print(f'Got {len(tx)} orders')
  print(json.dumps(tx, indent=2))

  with open(OUTPUT, 'w') as f:
    for row in tx:
      f.write(json.dumps(row) + '\n')

  #transactions.plotDistribution()

  return


if __name__ == "__main__":
    main()
