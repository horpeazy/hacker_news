from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ------------------------------------------------------------------#
# Models.
# ---------------------------------------------------- -------------#


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    hacker_news_id = db.Column(db.Integer)
    type = db.Column(db.String(20), nullable=False)
    time_posted = db.Column(db.DateTime)
    author = db.Column(db.String(120))
    deleted = db.Column(db.Boolean)
    dead = db.Column(db.Boolean)
    text = db.Column(db.String())
    url = db.Column(db.String())
    title = db.Column(db.String())
    parent = db.Column(db.Integer)
    parts = db.Column(db.PickleType)
    descedants = db.Column(db.Integer)
    score = db.Column(db.Integer)
    kids = db.Column(db.PickleType)

    def __repr__(self) -> str:
        return f'<Item: {self.id} Type: {self.type}>'

    def format(self):
        item = {}
        item['id'] = self.id
        item['type'] = self.type and self.type
        if self.time_posted:
            item['time'] = self.time_posted
        if self.author:
            item['by'] = self.author
        if self.deleted:
            item['deleted'] = self.deleted
        if self.dead:
            item['dead'] = self.dead
        if self.text:
            item['text'] = self.text
        if self.url:
            item['url'] = self.url
        if self.title:
            item['title'] = self.title
        if self.parent:
            item['parent'] = self.parent
        if self.parts:
            item['parts'] = self.parts
        if self.descedants:
            item['descedants'] = self.descedants
        if self.score:
            item['score'] = self.score
        if self.kids:
            item['kids'] = self.kids
        return item
