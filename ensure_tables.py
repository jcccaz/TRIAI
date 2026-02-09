from database import Base, engine, SystemEvent, Comparison, Response, QueryFeedback, ResponseEvaluation
print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
