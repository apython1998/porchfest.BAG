from app import app, db
from app.models import Porch, Porchfest, Artist, Show, Location


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Porch': Porch, 'Porchfest': Porchfest, 'Artist': Artist, 'Show': Show, 'Location':Location}