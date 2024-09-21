import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.metrics import jaccard_distance
from statistics import mean
import nltk
import multiprocessing as mp
from tqdm import tqdm 
from app.models import SimilarityScoreSchema
from sqlalchemy.orm import Session
from app.database import engine
from app.utils.background_task import sort_reviewers_based_on_mean_similarity



nltk.download('punkt')
nltk.download('punkt_tab')

def jaccard_partial_match(m_kp, p_kp):
    m_kp = set(word_tokenize(m_kp.lower()))
    p_kp = set(word_tokenize(p_kp.lower()))
    return 1 - jaccard_distance(m_kp, p_kp)


def jaccard(manuscript_kp, past_paper_kp, sim_args):
    if sim_args[1] == "cross":
        pos_factor = float(sim_args[6])
        similarity = 0
        for idx_m, m_kp in enumerate(manuscript_kp):
            sim = []
            for idx_p, p_kp in enumerate(past_paper_kp):
                pos = abs(idx_p - idx_m)
                sim_value = jaccard_partial_match(m_kp, p_kp) * 2 / (1 + np.exp(pos_factor * pos))
                sim.append(sim_value)
            
           
            if sim:
                similarity += max(sim)
            else:
                similarity += 0  
                
        return (similarity / len(manuscript_kp)) * 5 if manuscript_kp else 0  
    else:
        manuscript_kp = " ".join(manuscript_kp)
        past_paper_kp = " ".join(past_paper_kp)
        return jaccard_partial_match(manuscript_kp, past_paper_kp) * 5

def compute_similarity(manuscript_id, reviewer_id, manuscript_kp, reviewer_df, sim_args):
    reviewer_papers = reviewer_df[reviewer_df['reviewer_id'] == reviewer_id]
    similarity_scores = []

   
    for _, row in reviewer_papers.iterrows():
        paper_kp = row['keyphrases']
        paper_kp = str(paper_kp).split() if pd.notna(paper_kp) else []
        similarity_score = jaccard(manuscript_kp, paper_kp, sim_args)
        similarity_scores.append(similarity_score)

    
    if similarity_scores:
        mean_similarity = float(np.mean(similarity_scores))
    else:
        mean_similarity = 0.0

    return [int(manuscript_id), int(reviewer_id), mean_similarity]


def extract_similarities(db: Session):
    
    # reviewer_df = pd.read_csv("csv\\updated_reviewer_keyphrases_with_paper_id.csv")  
    # manuscript_df = pd.read_csv("csv\\manuscript_keyphrases2.csv")
    reviewer_df = pd.read_sql_table('reviewers_keyphrases',con=engine).head(10)
    manuscript_df = pd.read_sql_table('manuscripts_keyphrases',con=engine).head(10)
    
     

    sim_args = [None, "cross", None, None, None, None, 0.5]


    tasks = []
    for manuscript_id in manuscript_df['manuscript_id'].unique():
        manuscript_kp = manuscript_df.loc[manuscript_df['manuscript_id'] == manuscript_id, 'keyphrases'].fillna('').astype(str).values[0].split()

        for reviewer_id in reviewer_df['reviewer_id'].unique():
            tasks.append((manuscript_id, reviewer_id, manuscript_kp, reviewer_df, sim_args))

    print(len(tasks))
    with mp.Pool(mp.cpu_count()) as pool:
        results = list(tqdm(pool.starmap(compute_similarity, tasks), total=len(tasks)))

    
    similarity_records = []
    for result in results:
        manuscript_id, reviewer_id, mean_similarity = result
        similarity_records.append(SimilarityScoreSchema(
            manuscript_id=manuscript_id,
            reviewer_id=reviewer_id,
            mean_similarity=mean_similarity
        ))
    # result_df = pd.DataFrame(results, columns=['manuscript_id', 'reviewer_id', 'mean_similarity'])
    db.bulk_save_objects(similarity_records)
    db.commit()
    print("Similarity scores populated successfully")
    sort_reviewers_based_on_mean_similarity(db)
    print("Similarity scores sorted successfully")
    

if __name__ == "__main__":
    extract_similarities()