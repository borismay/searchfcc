import pandas as pd
from fuzzywuzzy import fuzz
import streamlit as st
from process_fcc_data import *
import re

# 499 form search
# https://apps.fcc.gov/cgb/form499/499a.cfm
# frn search
# https://apps.fcc.gov/coresWeb/simpleSearch.do?btnSearch=true

def search_sp(df, name, name_fields, score_th=97):
    # token_set_ratio is case insensitive
    scores = df[name_fields].applymap(lambda x: fuzz.token_set_ratio(x, name) >= score_th).any(axis=1)
    return df[scores]

def prepare_file():
    fcc499_df = pd.read_excel(r'c:\Python\boradband\499\RegistrationData.xlsx')
    fcc499_df = fcc499_df[~(fcc499_df['note1'].notna() | fcc499_df['note2'].notna() | fcc499_df['note3'].notna())]
    fcc499_df['Principal_Comm_Type_1'].value_counts().to_excel('sp_types.xls')
    sp_types = ['Interconnected Voip', 'Incumbent LEC', 'CAP/CLEC', 'Private Service Provider', 'Cellular/PCS/SMR', 'Interexchange Carrier']
    fcc499_df = fcc499_df[fcc499_df['Principal_Comm_Type_1'].isin(sp_types)]
    fcc499_df.reset_index(inplace=True)
    fcc499_df.to_excel('active_filtered_sp_499.xls')

@st.cache
def load_data():
    filename = r'active_filtered_sp_499.csv'
    return pd.read_csv(filename, engine='python')

def get_fcc_records(name):
    page = get_license_page(name)
    frns = get_frns(page)
    data = []
    for frn in frns:
        data.append(parse_frn(frn))
    return pd.DataFrame(data)

if __name__ == '__main__':
    df = load_data()

    name_fields = ['Legal_Name_of_Carrier', 'Doing_Business_As', 'Holding_Company', 'Management_Company'] + ['Other_Trade_Name{}'.format(n) for n in range(1, 14)]

    name = st.sidebar.text_input('SP name', '')
    score_th = st.sidebar.slider('Match score', 70, 100, value=97, step=1)

    display_fields_defaults = ['Legal_Name_of_Carrier', 'Doing_Business_As', 'Principal_Comm_Type_1', 'HQ_State', 'Holding_Company']
    display_fields = st.sidebar.multiselect('Display fields', df.columns.to_list(), display_fields_defaults)

    enhanced_search = st.sidebar.checkbox('Enable enhanced FCC search')

    st.title('Search results')
    if name:
        results_df = search_sp(df, name, name_fields, score_th)
        st.dataframe(results_df[display_fields])
        sp_names = results_df['Legal_Name_of_Carrier'].to_list()
        for name in sp_names:
            name_ = re.sub(r'[\.\,]', '', name)
            name_ = re.sub(r'\s&\s', '&', name_)
            st.subheader(name_)
            st.dataframe(get_fcc_records(name_).T)
            if enhanced_search:
                if len(name_.split(' ')) > 1:
                    name_ = name_.split(' ')[0]
                    st.subheader(name_)
                    st.dataframe(get_fcc_records(name_).T)

