import dash
import MySQLdb
from flask import Flask, request, session
from flask.helpers import get_root_path
from flask_bootstrap import Bootstrap, bootstrap_find_resource
from flask_login import LoginManager, login_required
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from urllib.parse import urlparse
from config import Config

__version__ = "v3.2.2"
boostrap = Bootstrap()
db = SQLAlchemy()
loginManager = LoginManager()
loginManager.session_protection = "basic"
loginManager.login_view = "authentications.login"
moment = Moment()

def createApp(configClass = Config):
	app = Flask(__name__)
	app.config.from_object(configClass)
	boostrap.init_app(app)

	from app.dashes.eventFramesSummary.layout import layout as eventFramesSummaryLayout
	from app.dashes.eventFramesSummary.callbacks import registerCallbacks as eventFramesSummaryCallbacks
	registerDashApp(app, "eventFramesSummaryDash", eventFramesSummaryLayout, eventFramesSummaryCallbacks, "Event Frames Summary Dash")

	from app.dashes.elementsSummary.layout import layout as elementsSummaryLayout
	from app.dashes.elementsSummary.callbacks import registerCallbacks as elementsSummaryCallbacks
	registerDashApp(app, "elementsSummaryDash", elementsSummaryLayout, elementsSummaryCallbacks, "Elements Summary")

	from app.dashes.elementsGraph.layout import layout as elementsGraphLayout
	from app.dashes.elementsGraph.callbacks import registerCallbacks as elementsGraphCallbacks
	registerDashApp(app, "elementsGraphDash", elementsGraphLayout, elementsGraphCallbacks, "Elements Graph")

	from app.dashes.eventFrameGroupSummary.layout import layout as eventFrameGroupSummaryLayout
	from app.dashes.eventFrameGroupSummary.callbacks import registerCallbacks as eventFrameGroupSummaryCallbacks
	registerDashApp(app, "eventFrameGroupSummaryDash", eventFrameGroupSummaryLayout, eventFrameGroupSummaryCallbacks, "Event Frame Group Summary")

	from app.dashes.eventFrameGraph.layout import layout as eventFrameGraphLayout
	from app.dashes.eventFrameGraph.callbacks import registerCallbacks as eventFrameGraphCallbacks
	registerDashApp(app, "eventFrameGraphDash", eventFrameGraphLayout, eventFrameGraphCallbacks, "Event Frame Graph")

	from app.dashes.eventFramesOverlay.layout import layout as eventFramesOverlayLayout
	from app.dashes.eventFramesOverlay.callbacks import registerCallbacks as eventFramesOverlayCallbacks
	registerDashApp(app, "eventFramesOverlayDash", eventFramesOverlayLayout, eventFramesOverlayCallbacks, "Event Frames Overlay")

	from app.dashes.tagValuesGraph.layout import layout as tagValuesGraphLayout
	from app.dashes.tagValuesGraph.callbacks import registerCallbacks as tagValuesGraphCallbacks
	registerDashApp(app, "tagValuesGraphDash", tagValuesGraphLayout, tagValuesGraphCallbacks, "Tag Values Graph")

	db.init_app(app)
	if app.config["IS_MULTI_TENANT"]:
		with app.app_context():
			@db.event.listens_for(db.engine, "do_connect")
			def receiveDoConnect(dialect, conn_rec, cargs, cparams):
				url = request.url_root
				subdomain = urlparse(url).hostname.split(".")[0]
				if subdomain != session.get("subdomain"):
					session["subdomain"] = subdomain
					connection = MySQLdb.connect(host = app.config["MULTI_TENANT_HOST"], db = app.config["MULTI_TENANT_DATABASE"],
						user = app.config["MULTI_TENANT_USERNAME"], passwd = app.config["MULTI_TENANT_PASSWORD"])
					cursor = connection.cursor()
					cursor.execute(f"SELECT HostName, DatabaseName, UserName, Password FROM Tenant WHERE Subdomain='{subdomain}'")
					results = cursor.fetchall()
					session["breweryPiHostName"] = results[0][0]
					session["breweryPiDatabaseName"] = results[0][1]
					session["breweryPiUserName"] = results[0][2]
					session["breweryPiPassword"] = results[0][3]

				cparams["host"] = session.get("breweryPiHostName")
				cparams["db"] = session.get("breweryPiDatabaseName")
				cparams["user"] = session.get("breweryPiUserName")
				cparams["passwd"] = session.get("breweryPiPassword")
				return None

	loginManager.init_app(app)
	moment.init_app(app)

	from . areas import areas as areasBlueprint
	app.register_blueprint(areasBlueprint)

	from . authentications import authentications as authenticationsBlueprint
	app.register_blueprint(authenticationsBlueprint)

	from . customTemplateFilters import customTemplateFilters as customTemplateFiltersBlueprint
	app.register_blueprint(customTemplateFiltersBlueprint)

	from . dashes import dashes as dashesBlueprint
	app.register_blueprint(dashesBlueprint)

	from . elements import elements as elementsBlueprint
	app.register_blueprint(elementsBlueprint)

	from . elementAttributes import elementAttributes as elementAttributesBlueprint
	app.register_blueprint(elementAttributesBlueprint)

	from . elementAttributeTemplates import elementAttributeTemplates as elementAttributeTemplatesBlueprint
	app.register_blueprint(elementAttributeTemplatesBlueprint)

	from . elementTemplates import elementTemplates as elementTemplatesBlueprint
	app.register_blueprint(elementTemplatesBlueprint)

	from . enterprises import enterprises as enterprisesBlueprint
	app.register_blueprint(enterprisesBlueprint)

	from . eventFrameAttributes import eventFrameAttributes as eventFrameAttributesBlueprint
	app.register_blueprint(eventFrameAttributesBlueprint)

	from . eventFrameAttributeTemplates import eventFrameAttributeTemplates as eventFrameAttributeTemplatesBlueprint
	app.register_blueprint(eventFrameAttributeTemplatesBlueprint)

	from . eventFrameEventFrameGroups import eventFrameEventFrameGroups as eventFrameEventFrameGroupsBlueprint
	app.register_blueprint(eventFrameEventFrameGroupsBlueprint)

	from . eventFrameGroups import eventFrameGroups as eventFrameGroupsBlueprint
	app.register_blueprint(eventFrameGroupsBlueprint)

	from . eventFrameNotes import eventFrameNotes as eventFrameNotesBlueprint
	app.register_blueprint(eventFrameNotesBlueprint)

	from . eventFrames import eventFrames as eventFramesBlueprint
	app.register_blueprint(eventFramesBlueprint)

	from . eventFramesOverlay import eventFramesOverlay as eventFramesOverlayBlueprint
	app.register_blueprint(eventFramesOverlayBlueprint)

	from . eventFrameTemplates import eventFrameTemplates as eventFrameTemplatesBlueprint
	app.register_blueprint(eventFrameTemplatesBlueprint)

	from . eventFrameTemplateViews import eventFrameTemplateViews as eventFrameTemplateViewsBlueprint
	app.register_blueprint(eventFrameTemplateViewsBlueprint)

	from . lookups import lookups as lookupsBlueprint
	app.register_blueprint(lookupsBlueprint)

	from . lookupValues import lookupValues as lookupValuesBlueprint
	app.register_blueprint(lookupValuesBlueprint)

	from . main import main as mainBlueprint
	app.register_blueprint(mainBlueprint)

	from . messages import messages as messagesBlueprint
	app.register_blueprint(messagesBlueprint)

	from . notifications import notifications as notificationsBlueprint
	app.register_blueprint(notificationsBlueprint)

	from . physicalModels import physicalModels as physicalModelsBlueprint
	app.register_blueprint(physicalModelsBlueprint)

	from . raspberryPiUtilities import raspberryPiUtilities as raspberryPiUtilitiesBlueprint
	app.register_blueprint(raspberryPiUtilitiesBlueprint)

	from . sites import sites as sitesBlueprint
	app.register_blueprint(sitesBlueprint)

	from . tags import tags as tagsBlueprint
	app.register_blueprint(tagsBlueprint)

	from . tagValueNotes import tagValueNotes as tagValueNotesBlueprint
	app.register_blueprint(tagValueNotesBlueprint)

	from . tagValues import tagValues as tagValuesBlueprint
	app.register_blueprint(tagValuesBlueprint)

	from . unitOfMeasurements import unitOfMeasurements as unitOfMeasurementsBlueprint
	app.register_blueprint(unitOfMeasurementsBlueprint)

	from . users import users as usersBlueprint
	app.register_blueprint(usersBlueprint)

	return app

def registerDashApp(app, urlBasePathname, layout, registerCallbacks, title):
	if app.config["BOOTSTRAP_SERVE_LOCAL"]:
		externalStylesheets = ["/static/bootstrap/css/bootstrap.min.css"]
		externalScripts = ["/static/bootstrap/jquery.min.js", "/static/bootstrap/js/bootstrap.min.js"]
	else:
		with app.app_context():
			externalStylesheets = [bootstrap_find_resource("css/bootstrap.css", cdn = "bootstrap")]
			externalScripts = [bootstrap_find_resource("jquery.js", cdn = "jquery"), bootstrap_find_resource("js/bootstrap.js", cdn = "bootstrap")]

	dashApp = dash.Dash \
	(
		__name__,
		assets_folder = "{}/{}/assets/".format(get_root_path(__name__), urlBasePathname),
		external_stylesheets = externalStylesheets,
		external_scripts = externalScripts,
		server = app,
		url_base_pathname = "/{}/".format(urlBasePathname)
	)

	dashApp.layout = layout
	dashApp.title = title
	registerCallbacks(dashApp)
	protectDashviews(dashApp)

def protectDashviews(dashApp):
	for viewFunction in dashApp.server.view_functions:
		if viewFunction.startswith(dashApp.config.url_base_pathname):
			dashApp.server.view_functions[viewFunction] = login_required(dashApp.server.view_functions[viewFunction])
