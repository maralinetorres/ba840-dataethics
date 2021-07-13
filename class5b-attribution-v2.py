#!/usr/bin/env python
# coding: utf-8


import pandas as pd, numpy as np, os, warnings, seaborn as sns, matplotlib.pyplot as plt, matplotlib
from datetime import datetime

warnings.simplefilter(action='ignore', category=FutureWarning) 
pd.options.mode.chained_assignment = None
get_ipython().run_line_magic('matplotlib', 'inline')
plt.style.use('seaborn')
sns.set_color_codes('colorblind')
matplotlib.rcParams.update({'font.size': 14}) 
matplotlib.rcParams.update({'xtick.labelsize':16})
matplotlib.rcParams.update({'ytick.labelsize':16})
matplotlib.rcParams.update({'axes.labelsize':16})
matplotlib.rcParams.update({'axes.titlesize':20})
matplotlib.rcParams.update({'legend.fontsize': 16}) 

sns.set_style('white')

# install this if read_excel reports error
# !pip3 install openpyxl



DF = pd.read_excel('PS21/PS3/attribution-data.xlsx', engine="openpyxl")
DF.head()



# Simple summary

print('Time range: ', DF['Order Date Time'].min(), 'to', DF['Order Date Time'].max())
print('Number of touchpoints:', len(DF))
print('Number of orders:', len(DF['Order Id'].unique()))
print('Number of touchpoints per order:', np.round(len(DF)/len(DF['Order Id'].unique()), 2))


# ### Note: 
# The same order is counted as multiple observations. For most order-level stats, we will want to do some filtering to avoid double-counting. 

# "Position" tags the first touchpoint for each order. Can use that to filter.
# Alternatively, use "Position name" to filter
np.round(DF.loc[DF['Position']==0, 'Sale Amount'].describe(), 3)

# Distribution of sales per order
DF.loc[DF['Position']==0, 'Sale Amount'].hist(bins=30)

# Distribution of new vs. old customers
DF.loc[DF['Position']==0, 'New Customer'].value_counts()


# ### Task 1: Last-touch attribution to channels. 
# To do this, filter data to include only the last touch, then count ther percentage of channels. 
num_order = len(DF['Order Id'].unique())
T_last = pd.DataFrame(DF.loc[DF['Position Name']=='CONVERTER', 
                             'Group Name'].value_counts()/num_order).reset_index().sort_values('index')
np.round(T_last,3)


# ### Task 2: First-touch Attribution
T_first = pd.DataFrame(DF.loc[DF['Position Name']=='ORIGINATOR', 
                              'Group Name'].value_counts()/num_order).reset_index().sort_values('index')
np.round(T_first, 3)


# To compare, combine the two tables so that order of channels are aligned
np.round(pd.merge(T_first, T_last, how = 'outer', on = 'index').fillna(0).rename(
    columns={"Group Name_x": "Credit_first", "Group Name_y": "Credit_last"}), 3)


# ### 3. Discussion: 
# - What channels do first-touch attribute more credits to? 
# - What channels do last-touch attribute more credits to?
# - What may be possible reasons that drive this pattern?
# * Note 1: many all user-initiated journeys (that end with a purchase) start with search
# * Note 2: many CPM (display ad) here are retargeting campaigns (e.g. those from adroll)

# ### Task 4: What if we just focus on new customers?
num_order_new = len(DF[(DF['Position Name']=='CONVERTER')&(DF['New Customer'] == 'Y')])
num_order_old = len(DF[(DF['Position Name']=='CONVERTER')&(DF['New Customer'] == 'N')])

T_last_new = pd.DataFrame(DF.loc[(DF['Position Name']=='CONVERTER')&(DF['New Customer'] == 'Y'), 
                'Group Name'].value_counts()/num_order_new).reset_index().sort_values('index')

T_first_new = pd.DataFrame(DF.loc[(DF['Position Name']=='ORIGINATOR')&(DF['New Customer'] == 'Y'), 
                'Group Name'].value_counts()/num_order_new).reset_index().sort_values('index')

np.round(pd.merge(T_first_new, T_last_new, how = 'outer', on = 'index').fillna(0).rename(
    columns={"Group Name_x": "Credit_first", "Group Name_y": "Credit_last"}), 3)


# Old customers

T_last_old = pd.DataFrame(DF.loc[(DF['Position Name']=='CONVERTER')&(DF['New Customer'] == 'N'), 
                'Group Name'].value_counts()/num_order_old).reset_index().sort_values('index')

T_first_old = pd.DataFrame(DF.loc[(DF['Position Name']=='ORIGINATOR')&(DF['New Customer'] == 'N'), 
                'Group Name'].value_counts()/num_order_old).reset_index().sort_values('index')

np.round(pd.merge(T_first_old, T_last_old, how = 'outer', on = 'index').fillna(0).rename(
    columns={"Group Name_x": "Credit_first", "Group Name_y": "Credit_last"}), 3)


# ### Task 5: Time decay model

# Create credits based on formula
# Non-normalized credits
DF['t_decay_credit'] = pow(2, (- DF['Time to Convert (Days)']/7))

# Normalize so that credits for each order sums to 1
grouped = DF[['Order Id','t_decay_credit']].groupby('Order Id')
DF['t_decay_credit_normed'] = grouped.transform(lambda x: x/sum(x))

# Sanity check:
# DF[['Order Id','t_decay_credit_normed']].groupby('Order Id').sum()

# Now sum normalized credits across channels & normalize
T_tdecay = pd.DataFrame(DF[['Group Name', 't_decay_credit_normed']].groupby('Group Name').sum()/num_order).reset_index()

np.round(T_tdecay, 3)


# Merge time-decay & last-touch to compare
np.round(pd.merge(T_tdecay , T_last.rename(columns={"Group Name": "Credit_last", "index": "Group Name"}), 
                 how = 'outer', on = 'Group Name').fillna(0).rename(
                 columns={"t_decay_credit_normed": "Credit_time_decay"}), 3)


# In[ ]:




