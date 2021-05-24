from flask import render_template
from app import __version__
from app.main import main
from app.models import Enterprise, EventFrameGroup

@main.route("/")
def index():
	version = __version__
	enterprises = Enterprise.query.all()
	eventFrameGroups = EventFrameGroup.query.all()
	return render_template("main/index.html", enterprises = enterprises, eventFrameGroups = eventFrameGroups, version = version)
