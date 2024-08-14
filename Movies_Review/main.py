from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,IntegerField,FloatField
from wtforms.validators import DataRequired
import requests


url = "https://api.themoviedb.org/3/search/movie"

# go to this website https://api.themoviedb.org/ and create you account you will get
# headers = {
#     "accept": "",
#     "Authorization": ""
# }

app = Flask(__name__)
app.config['SECRET_KEY'] = ''#Create you own key
bootstrap=Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
# initialize the app with the extension

# CREATE DB
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
# CREATE TABLE

class EditForm(FlaskForm):
    rating = FloatField(label='Your Rating out of 10', validators=[DataRequired()])
    review = StringField(label='Review', validators=[DataRequired()])
    submit=SubmitField(label='Update')

class AddForm(FlaskForm):
    movie_title = StringField(label='Movie Title', validators=[DataRequired()])
    add_movie=SubmitField(label='Add Movie')

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    title: Mapped[str] = mapped_column(String(250),unique=True,nullable=False)
    year: Mapped[int]=mapped_column(Integer,nullable=False)
    description: Mapped[str]=mapped_column(String(500),nullable=False)
    rating: Mapped[float]=mapped_column(Float,nullable=True)
    ranking:Mapped[int]=mapped_column(Integer,nullable=True)
    review:Mapped[str]=mapped_column(String(250),nullable=True)
    img_url: Mapped[str]=mapped_column(String(250),nullable=False)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html",movies=all_movies)

@app.route('/update',methods=["POST","GET"])
def update():
    form=EditForm()
    movie_id=request.args.get('id')
    movie=db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating=float(form.rating.data)
        movie.review=form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',form=form,title=movie.title)
@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie=db.get_or_404(Movie,movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add',methods=["POST","GET"])
def add():
    form=AddForm()
    if form.validate_on_submit():
        title=form.movie_title.data
        param={
            "query":title
        }
        response = requests.get(url, headers=headers,params=param)
        result=response.json()['results']
        return render_template('select.html',movies=result)
    return render_template('add.html',form=form)

@app.route('/find')
def find_movie():
    movie_id = request.args.get('movie_id')
    print(id)
    if movie_id:
        MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
        response=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}",headers=headers)
        movie_info=response.json()
        new_movie=Movie(
            title=movie_info['original_title'],
            year=int(movie_info['release_date'].split("-")[0]),
            img_url=f"{MOVIE_DB_IMAGE_URL}{movie_info['poster_path']}",
            description=movie_info['overview'],
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('update',id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)


# new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
