import pandas as pd
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
import nltk
from sqlalchemy.orm import Session
from tqdm import tqdm
from app.models import table_name_to_model
from app.database import engine


nltk.download('punkt', quiet=True)

kw_model = KeyBERT()

def patternrank_keywords(title: str = None, abstract: str = None):
    title = str(title) if pd.notna(title) else ""
    abstract = str(abstract) if pd.notna(abstract) else ""

    text = title + " " + abstract if title and abstract else title or abstract

    try:
        top_n = 15
        keywords = kw_model.extract_keywords(text, vectorizer=KeyphraseCountVectorizer(), top_n=top_n)
        keyphrases = [words[0] for words in keywords]
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []

    length_keyphrases = 0
    for idx, keyphrase in enumerate(keyphrases):
        length_keyphrases += len(keyphrase)
        if "-" in keyphrase:
            keyphrases[idx] = keyphrase.replace("-", " ")

        if length_keyphrases >= 900:
            keyphrases = keyphrases[:idx]
            break

    return keyphrases

def extract_keyphrases(db: Session, table_name):
    try:
        table_columns = {
            'reviewers_keyphrases': ['paper_id', 'reviewer_id', 'title', 'abstract'],
            'manuscripts_keyphrases': ['manuscript_id', 'Title', 'Abstract']
        }
        
        columns = table_columns.get(table_name)
        df = pd.read_sql_table('papers', con=engine, columns=columns) if table_name == 'reviewers_keyphrases' else pd.read_sql_table('manuscripts', con=engine, columns=columns)
        model = table_name_to_model[table_name]
        
        records = []
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows"):
            if table_name == 'reviewers_keyphrases':
                paper_id = row.get('paper_id', '')
                reviewer_id = row.get('reviewer_id', '')
                title = row.get('title', '')
                abstract = row.get('abstract', '')

                keyphrases = patternrank_keywords(title=title, abstract=abstract)

                results = {
                    'paper_id': paper_id,
                    'reviewer_id': reviewer_id,
                    'title': title,
                    'keyphrases': ', '.join(keyphrases)
                }
            else:
                manuscript_id = row.get('manuscript_id', '')
                title = row.get('Title', '')
                abstract = row.get('Abstract', '')

                keyphrases = patternrank_keywords(title=title, abstract=abstract)

                results = {
                    'manuscript_id': manuscript_id,
                    'title': title,
                    'keyphrases': ', '.join(keyphrases)
                }
            new_record = model(**results)
            records.append(new_record)
            
        db.bulk_save_objects(records)
        db.commit()
        print(f"{table_name} keyphrases extracted successfully")
    except Exception as e:
        print(f"Error: {e}")
        return

if __name__ == "__main__":
    extract_keyphrases(db=engine)