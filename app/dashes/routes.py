from flask import render_template
from flask_login import login_required
from app.models import Element, ElementAttribute, ElementTemplate, EventFrame, EventFrameGroup, EventFrameTemplate, Site, Tag
from . import dashes

@dashes.route("/dashes/activeEventFramesSummary", methods = ["GET", "POST"])
@dashes.route("/dashes/activeEventFramesSummary/site/<int:siteId>", methods = ["GET", "POST"])
@dashes.route("/dashes/activeEventFramesSummary/elementTemplate/<int:elementTemplateId>", methods = ["GET", "POST"])
@dashes.route("/dashes/activeEventFramesSummary/eventFrameTemplate/<int:eventFrameTemplateId>", methods = ["GET", "POST"])
@login_required
def activeEventFramesSummary(siteId = None, elementTemplateId = None, eventFrameTemplateId = None):
	site = None
	elementTemplate = None
	eventFrameTemplate = None
	if siteId is not None:
		site = Site.query.filter_by(SiteId = siteId).one_or_none()
	elif elementTemplateId is not None:
		elementTemplate = ElementTemplate.query.filter_by(ElementTemplateId = elementTemplateId).one_or_none()
	elif eventFrameTemplateId is not None:
		eventFrameTemplate = EventFrameTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateId).one_or_none()

	return render_template("dashes/activeEventFramesSummary/activeEventFramesSummary.html", elementTemplate = elementTemplate,
		eventFrameTemplate = eventFrameTemplate, site = site)

@dashes.route("/dashes/elementsSummary", methods = ["GET", "POST"])
@dashes.route("/dashes/elementsSummary/site/<int:siteId>", methods = ["GET", "POST"])
@dashes.route("/dashes/elementsSummary/elementTemplate/<int:elementTemplateId>", methods = ["GET", "POST"])
@login_required
def elementsSummary(siteId = None, elementTemplateId = None):
	site = None
	elementTemplate = None
	if siteId is not None:
		site = Site.query.filter_by(SiteId = siteId).one_or_none()
	elif elementTemplateId is not None:
		elementTemplate = ElementTemplate.query.filter_by(ElementTemplateId = elementTemplateId).one_or_none()

	return render_template("dashes/elementsSummary/elementsSummary.html", elementTemplate = elementTemplate, site = site)

@dashes.route("/dashes/elementsGraph", methods = ["GET", "POST"])
@dashes.route("/dashes/elementsGraph/<int:elementId>", methods = ["GET", "POST"])
@login_required
def elementsGraph(elementId = None):
	element = None
	if elementId is not None:
		element = Element.query.filter_by(ElementId = elementId).one_or_none()

	return render_template("dashes/elementsGraph/elementsGraph.html", element = element)

@dashes.route("/dashes/eventFrameGroupSummary", methods = ["GET", "POST"])
@dashes.route("/dashes/eventFrameGroupSummary/<int:eventFrameGroupId>", methods = ["GET", "POST"])
@login_required
def eventFrameGroupSummary(eventFrameGroupId = None):
	eventFrameGroup = None
	if eventFrameGroupId is not None:
		eventFrameGroup = EventFrameGroup.query.filter_by(EventFrameGroupId = eventFrameGroupId).one_or_none()

	return render_template("dashes/eventFrameGroupSummary/eventFrameGroupSummary.html", eventFrameGroup = eventFrameGroup)

@dashes.route("/dashes/eventFrameGraph", methods = ["GET", "POST"])
@dashes.route("/dashes/eventFrameGraph/<int:eventFrameId>", methods = ["GET", "POST"])
@login_required
def eventFrameGraph(eventFrameId = None):
	eventFrame = None
	if eventFrameId is not None:
		eventFrame = EventFrame.query.filter_by(EventFrameId = eventFrameId).one_or_none()

	return render_template("dashes/eventFrameGraph/eventFrameGraph.html", eventFrame = eventFrame)

@dashes.route("/dashes/eventFramesOverlay", methods = ["GET", "POST"])
@login_required
def eventFramesOverlay():
	return render_template("dashes/eventFramesOverlay/eventFramesOverlay.html")

@dashes.route("/dashes/tagValuesGraph", methods = ["GET", "POST"])
@dashes.route("/dashes/tagValuesGraph/elementAttribute/<int:elementAttributeId>", methods = ["GET", "POST"])
@dashes.route("/dashes/tagValuesGraph/tag/<int:tagId>", methods = ["GET", "POST"])
@login_required
def tagValuesGraph(elementAttributeId = None, tagId = None):
	elementAttribute = None
	tag = None
	if elementAttributeId is not None:
		elementAttribute = ElementAttribute.query.filter_by(ElementAttributeId = elementAttributeId).one_or_none()
	elif tagId is not None:
		tag = Tag.query.filter_by(TagId = tagId).one_or_none()
	return render_template("dashes/tagValuesGraph/tagValuesGraph.html", elementAttribute = elementAttribute, tag = tag)
