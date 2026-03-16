#!/usr/bin/env python
# coding: utf-8

# In[31]:


import pandas as pd


# In[32]:


from glob import glob


# In[33]:


dfs = []
for fname in glob('*.json'):
    dfs.append(pd.read_json(fname, lines=True))
df = pd.concat(dfs)


# In[34]:


s = set(df['id'].tolist())


# In[35]:


bdf = df.groupby(["id"]).agg(min_date=('date', 'min'), max_date=('date', 'max'))


# In[36]:


df1 = df.merge(bdf, on=["id"])


# In[48]:


min_df = df1.loc[df1["min_date"] == df1["date"]][['id', 'followers','date']]


# In[52]:


max_df = df1.loc[df1["max_date"] == df1["date"]][['id', 'followers', 'date']]


# In[53]:


min_df = min_df.rename(columns={'followers':'baseline_followers'})
max_df = max_df.rename(columns={'followers':'current_followers'})


# In[54]:


max_df


# In[40]:


rdf = min_df.merge(max_df, on='id')


# In[41]:


rdf['change'] = (rdf['current_followers'] - rdf['baseline_followers']) / rdf['current_followers'] * 100


# In[42]:


rdf


# In[59]:


rdf.merge(df, on='id')[['id','name', 'baseline_followers', 'current_followers', 'change']]


# In[60]:


odf = pd.read_json('../toquery_updated_v2.json')


# In[61]:


odf.head()


# In[104]:


result_df = odf.merge(rdf, on='id')


# In[ ]:


from plotly.offline import init_notebook_mode, iplot
from plotly import graph_objs as go
init_notebook_mode(connected = True)


# In[111]:


result_df.sort_values(by=['category', 'name'])


# In[112]:


data = [
    go.Bar(y=result_df['name'], x=result_df['current_followers'], name='Current', width=1, orientation='h'),
    go.Bar(y=result_df['name'], x=result_df['baseline_followers'], name='Baseline', width=0.25, orientation='h'),
    
]
layout = go.Layout(barmode='overlay')


# In[114]:


fig = dict(data = data, layout = layout)
iplot(fig, show_link=False)


# In[ ]:




