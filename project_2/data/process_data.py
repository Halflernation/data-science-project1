import sys
### Pandas
import pandas as pd
### SQL Alchemy
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    # load data from database
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    # merge
    df = messages.merge(categories, on='id')
    # print(df)
    return df

def clean_data(df):
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='any')
    
    categories = df['categories'].str.split(';', expand=True)
    
    row = categories.loc[0,:]
    category_colnames = row.apply(lambda col: col[:-2])
    categories.columns = category_colnames
    
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str.slice(-1)
    
        # convert column from string to numeric
        categories[column] = categories[column].astype(str)
        
        # Remove everything not 0s and 1s
        categories[column] = categories[column][categories[column].isin(['0', '1'])]
    
    # drop NA values (there are some present)
    categories.dropna(how='any', inplace=True)
    
    # drop the original categories column from `df`
    df = df.drop(labels='categories', axis=1)
    
    # concatenate the original dataframe with the new `categories` dataframe
    df = df.merge(categories, left_index=True, right_index=True)
    
    # Drop duplicates
    df = df.drop_duplicates()
    return df

def save_data(df, database_filename):
    engine = create_engine('sqlite:///'+database_filename)
    df.to_sql('messages', engine, index=False, if_exists='replace')


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        print(df)
        print('Cleaned data saved to database!')
        print('DataFrame size: {}'.format(df.count(axis=1)))
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
