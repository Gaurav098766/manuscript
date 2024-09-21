from sqlalchemy import text
from app.models import table_name_to_model
from sqlalchemy.orm import Session 


def populate_paper_reviews(db: Session):
    try:
        query = """SELECT reviewers.reviewer_id, papers.paper_id FROM reviewers INNER JOIN papers ON reviewers.reviewer_id = papers.reviewer_id"""
        join_results = db.execute(text(query)).fetchall()
        
        paper_reviewers_model = table_name_to_model['paper_reviewers']
        
        for row in join_results:
            reviewer_id, paper_id = row
            new_paper_reviewer = paper_reviewers_model(reviewer_id=reviewer_id, paper_id=paper_id)
            db.add(new_paper_reviewer)
        
        db.commit()
        print("Paper reviews populated successfully")
    except Exception as e:
        print(f"Error while populating paper_reviews: {e}")


def sort_reviewers_based_on_mean_similarity(db: Session):
    try:
        query="""WITH ranked_reviewers AS (
                    SELECT 
                        manuscript_id, 
                        reviewer_id, 
                        mean_similarity,
                        ROW_NUMBER() OVER (PARTITION BY manuscript_id ORDER BY mean_similarity DESC) AS rank
                    FROM similarity_scores
                )
                    SELECT 
                        manuscript_id, 
                        reviewer_id, 
                        mean_similarity
                    FROM ranked_reviewers
                    WHERE rank <= 10;
            """
        db.execute(text(query))
        db.commit()
    except Exception as e:
        print("Error:",e)
        
        

def get_reviewer_name_from_manuscript_id(db: Session):
    try:
        query = """SELECT similarity_scores.manuscript_id, similarity_scores.reviewer_id, reviewers.name
                FROM similarity_scores
                INNER JOIN reviewers ON similarity_scores.reviewer_id = reviewers.reviewer_id;
                """
        db.execute(text(query))
        db.commit()
    except Exception as e:
        print("Error:", e)