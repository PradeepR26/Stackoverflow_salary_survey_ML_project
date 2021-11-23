import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from predict_page import load_model


def shorten_categories(categories, cutoff):
    categorical_map = {}
    for i in range(len(categories)):
        if categories.values[i] >= cutoff:
            categorical_map[categories.index[i]] = categories.index[i]
        else:
            categorical_map[categories.index[i]] = 'Other'
    return categorical_map

def clean_exp(x):
    if x == 'Less than 1 year':
        return 0.5
    elif x == 'More than 50 years':
        return 50
    else:
        return float(x)

def clean_edu(x):
    if "Bachelor’s degree" in x:
        return "Bachelor’s degree"
    elif "Master’s degree" in x:
        return "Master’s degree"
    elif 'Professional degree' in x or 'Other doctoral degree' in x:
        return 'Post graduate'
    else:
        return 'Less than a Bachlor degree'

@st.cache
def load_data():
    df = pd.read_csv('survey_results_public.csv')
    df = df[['Country', 'EdLevel', 'YearsCodePro', 'Employment', 'ConvertedCompYearly']]
    df = df.rename({'ConvertedCompYearly':'Salary'},axis=1)
    df = df[df['Salary'].notnull()]
    df = df.drop(df[df.isna().sum(axis=1)>0].index,axis=0)
    df = df[df['Employment']=='Employed full-time']
    df = df.drop('Employment',axis=1)

    country_map = shorten_categories(df.Country.value_counts(), 400)
    df['Country'] = df['Country'].map(country_map)

    high=0
    for i in df['Country'].unique():
        temp = (df[df['Country']==i]['Salary'].describe(percentiles =[0,0.95] ))[6]
        if temp>high:
            high=temp
    df = df[(df['Salary']>=1000)&(df['Salary']<=high)]

    df['YearsCodePro']=df['YearsCodePro'].apply(clean_exp)
    df['EdLevel'] = df['EdLevel'].apply(clean_edu)
    
    

    return df

df = load_data()

def show_explore_page():
    
    st.title('Explore Software Engineer Salaries')

    st.write(""" ### Stack Overflow Developer Survey 2021 """)

    # Plotting pie plot
    pie_data = df['Country'].value_counts()
    
    fig1, ax1 = plt.subplots()
    ax1.pie(pie_data, labels= pie_data.index, autopct="%1.1f%%", shadow=True, startangle=90)
    ax1.axis('equal') # Equal aspect ration will ensures that pie is drawn in circle.

    st.write("""#### Number of data from different countries""")

    st.pyplot(fig1)

    # Ploting bar chart
    st.write("""#### Mean salary based on countries""")

    bar_data = df.groupby(['Country'])['Salary'].mean().sort_values(ascending=True)
    
    st.bar_chart(bar_data)

    # Ploting line chart

    st.write("Mean salary based on experience")

    line_data = df.groupby(['YearsCodePro'])['Salary'].mean().sort_values(ascending=True)

    st.line_chart(line_data)
