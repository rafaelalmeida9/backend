from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Movie(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str = Field(unique=True)
    genre: str = Field(default=None)

movie_1 = Movie(title="Deadpond", genre="Adventure")
movie_2 = Movie(title="Spider-Boy", genre="Pizza delivery and photographer boy")
movie_3 = Movie(title="Rusty-Man", genre="Tony Stank")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        # session.add(movie_1)
        # session.add(movie_2)
        # session.add(movie_3)
        # session.commit()
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

create_db_and_tables()

@app.get("/movies")
async def get_movies(session: SessionDep,) -> list[Movie]:
    movies = session.exec(select(Movie)).all()
    return movies

@app.post("/movies")
async def create_movie(movie: Movie, session: SessionDep) -> Movie:
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return movie

@app.get("/movies/{movie_id}")
async def get_movie(movie_id: int, session: SessionDep):
    movie = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie
