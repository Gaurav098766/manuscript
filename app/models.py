from .database import Base
from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint, Float


class ReviewersSchema(Base):
    __tablename__ = "reviewers"

    reviewer_id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = Column(Text, nullable=False)
    affiliation = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    

class ManuscriptSchema(Base):
    __tablename__ = "manuscripts"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    manuscript_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    Title = Column(Text, nullable=False)
    Abstract = Column(Text, nullable=True)
    
    

class PapersSchema(Base):
    __tablename__ = "papers"
    
    paper_id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    reviewer_id = Column(Integer, ForeignKey('reviewers.reviewer_id', ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    
    # select reviewers.reviewer_id, papers.paper_id from reviewers inner join papers on reviewers.reviewer_id=papers.reviewer_id
    

class PaperReviewerSchema(Base):
    __tablename__ = "paper_reviewers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('reviewers.reviewer_id', ondelete="CASCADE"), nullable=False, index=True)
    paper_id = Column(Integer, ForeignKey('papers.paper_id', ondelete="CASCADE"), nullable=False, index=True, unique=True)

    __table_args__ = (UniqueConstraint('reviewer_id', 'paper_id', name='unique_reviewer_paper'),)


class ReviewerKeyphrasesSchema(Base):
    __tablename__ = "reviewers_keyphrases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('reviewers.reviewer_id', ondelete="CASCADE"), nullable=False, index=True)
    paper_id = Column(Integer, ForeignKey('papers.paper_id', ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    keyphrases = Column(Text, nullable=False)
    
    
class ManuscriptKeyphrasesSchema(Base):
    __tablename__ = "manuscripts_keyphrases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.manuscript_id', ondelete="CASCADE"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    keyphrases = Column(Text, nullable=False)
    

class SimilarityScoreSchema(Base):
    __tablename__ = "similarity_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewer_id = Column(Integer, ForeignKey('reviewers.reviewer_id', ondelete="CASCADE"), nullable=False, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.manuscript_id', ondelete="CASCADE"), nullable=False, index=True)
    mean_similarity = Column(Float, nullable=False)



table_name_to_model = {
    "reviewers": ReviewersSchema,
    "papers": PapersSchema,
    "paper_reviewers": PaperReviewerSchema,
    "manuscripts": ManuscriptSchema,
    "reviewers_keyphrases": ReviewerKeyphrasesSchema,
    "manuscripts_keyphrases": ManuscriptKeyphrasesSchema,
    "similarity_scores": SimilarityScoreSchema
}