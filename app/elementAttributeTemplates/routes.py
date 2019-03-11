from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from . import elementAttributeTemplates
from . forms import ElementAttributeTemplateForm
from .. import db
from .. decorators import adminRequired
from .. models import Area, ElementAttribute, ElementAttributeTemplate, ElementTemplate, Enterprise, EventFrameAttributeTemplate, Site, Tag

@elementAttributeTemplates.route("/elementAttributeTemplates/add/<int:elementTemplateId>", methods = ["GET", "POST"])
@elementAttributeTemplates.route("/elementAttributeTemplates/add/<int:elementTemplateId>/<int:lookup>", methods = ["GET", "POST"])
@login_required
@adminRequired
def addElementAttributeTemplate(elementTemplateId, lookup = False):
	operation = "Add"
	form = ElementAttributeTemplateForm()
	elementTemplate = ElementTemplate.query.get_or_404(elementTemplateId)

	if lookup:
		modelName = "Lookup Element Attribute Template"
		del form.unitOfMeasurement
	else:
		modelName = "Element Attribute Template"
		del form.lookup

	# Add a new elementAttributeTemplate.
	if form.validate_on_submit():
		if lookup:
			elementAttributeTemplate = ElementAttributeTemplate(Description = form.description.data, ElementTemplateId = form.elementTemplateId.data, \
				Lookup = form.lookup.data, Name = form.name.data)
		else:
			elementAttributeTemplate = ElementAttributeTemplate(Description = form.description.data, ElementTemplateId = form.elementTemplateId.data, \
				Name = form.name.data, UnitOfMeasurement = form.unitOfMeasurement.data)

		db.session.add(elementAttributeTemplate)
		db.session.commit()
		flash('You have successfully added the new element attribute template "{}".'.format(elementAttributeTemplate.Name), "alert alert-success")
		createdTags = []
		updatedTags = []
		createdElementAttributes = []
		for element in elementTemplate.Elements:
			if element.isManaged():
				# Tag management.
				area = Area.query.get_or_404(element.TagAreaId)
				tagName = "{}_{}".format(element.Name, elementAttributeTemplate.Name.replace(" ", ""))
				tag = Tag.query.filter_by(AreaId = area.AreaId, Name = tagName).one_or_none()
				if tag is None:
					# Tag doesn't exist, so create it.
					tag = Tag(AreaId = area.AreaId, LookupId = elementAttributeTemplate.LookupId, Name = tagName,
						UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)
					db.session.add(tag)
					createdTags.append(tag)
				else:
					# Tag exists, so update LookupId and UnitOfMeasurementId just in case.
					tag.LookupId = elementAttributeTemplate.LookupId
					tag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					updatedTags.append(tag)

				db.session.commit()

				# Element attribute management.
				elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
					ElementId = element.ElementId, TagId = tag.TagId)
				db.session.add(elementAttribute)
				db.session.commit()
				createdElementAttributes.append(elementAttribute)

		createdTagsMessage = ""
		if createdTags:
			createdTags.sort(key = lambda tag: tag.Name)
			for tag in createdTags:
				if createdTagsMessage == "":
					createdTagsMessage = 'Created the following tag(s):<br>"{}"'.format(tag.Name)
					alert = "alert alert-success"
				else:
					createdTagsMessage = '{}<br>"{}"'.format(createdTagsMessage, tag.Name)

			flash(createdTagsMessage, alert)

		updatedTagsMessage = ""
		if updatedTags:
			updatedTags.sort(key = lambda tag: tag.Name)
			for tag in updatedTags:
				if updatedTagsMessage == "":
					updatedTagsMessage = 'Updated the following existing tag(s), if needed:<br>"{}"'.format(tag.Name)
					alert = "alert alert-warning"
				else:
					updatedTagsMessage = '{}<br>"{}"'.format(updatedTagsMessage, tag.Name)

			flash(updatedTagsMessage, alert)

		createdElementAttributesMessage = ""
		if createdElementAttributes:
			createdElementAttributes.sort(key = lambda tag: tag.Element.Name)
			for elementAttribute in createdElementAttributes:
				if createdElementAttributesMessage == "":
					createdElementAttributesMessage = "Created the following element attribute(s):<br>Element: " + \
						'{}" attribute: "{}" associated with tag: "{}"'.format(elementAttribute.Element.Name, elementAttribute.ElementAttributeTemplate.Name,
						elementAttribute.Tag.Name)
					alert = "alert alert-success"
				else:
					createdElementAttributesMessage = '{}<br>Element: "{}" attribute: "{}" associated with tag: "{}"'.format(createdElementAttributesMessage,
						elementAttribute.Element.Name, elementAttribute.ElementAttributeTemplate.Name, elementAttribute.Tag.Name)

			flash(createdElementAttributesMessage, alert)

		# Event frame attribute template management.
		# Loop through all event frame template hierarchies checking for an event frame attribute template with the same event frame attribute template name.
		updatedEventFrameAttributeTemplates = []
		for topLevelEventFrameTemplate in elementAttributeTemplate.ElementTemplate.EventFrameTemplates:
			for eventFrameTemplate in topLevelEventFrameTemplate.descendants([], 0):
				newEventFrameAttributeTemplate = EventFrameAttributeTemplate.query. \
					filter_by(EventFrameTemplateId = eventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId,
					Name = elementAttributeTemplate.Name).one_or_none()
				if newEventFrameAttributeTemplate is not None:
				# New event frame attribute template exists, so update LookupId and UnitOfMeasurementId just in case.
					newEventFrameAttributeTemplate.lookupId = elementAttributeTemplate.LookupId
					newEventFrameAttributeTemplate.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					updatedEventFrameAttributeTemplates.append(newEventFrameAttributeTemplate)

		db.session.commit()

		updatedEventFrameAttributeTemplatesMessage = ""
		if updatedEventFrameAttributeTemplates:
			updatedEventFrameAttributeTemplates.sort(key = lambda eventFrameAttributeTemplate: eventFrameAttributeTemplate.path())
			for eventFrameAttributeTemplate in updatedEventFrameAttributeTemplates:
				if updatedEventFrameAttributeTemplatesMessage == "":
					updatedEventFrameAttributeTemplatesMessage = "Updated the following event frame attribute templates(s), if needed:<br>" + \
						'"{}\{}"'.format(eventFrameAttributeTemplate.path(), eventFrameAttributeTemplate.Name)
					alert = "alert alert-warning"
				else:
					updatedEventFrameAttributeTemplatesMessage = '{}<br>"{}\{}"'. \
						format(updatedEventFrameAttributeTemplatesMessage, eventFrameAttributeTemplate.path(), eventFrameAttributeTemplate.Name)

			flash(updatedEventFrameAttributeTemplatesMessage, alert)

		return redirect(form.requestReferrer.data)

	# Present a form to add a new element attribute template.
	form.elementTemplateId.data = elementTemplateId
	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"),
		"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise", selectedId = elementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementTemplate.Site.SiteId),
			"text" : elementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementAttributeTemplate", selectedId = elementTemplate.ElementTemplateId),
			"text" : elementTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)

@elementAttributeTemplates.route("/elementAttributeTemplates/delete/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def deleteElementAttributeTemplate(elementAttributeTemplateId):
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	tags = []
	for elementAttribute in elementAttributeTemplate.ElementAttributes:
		if elementAttribute.Element.isManaged():
			tags.append(elementAttribute.Tag)

	elementAttributeTemplate.delete()
	db.session.commit()
	flash('You have successfully deleted the element attribute template "{}".'.format(elementAttributeTemplate.Name), "alert alert-success")
	deletedTagsMessage = ""
	tags.sort(key = lambda tag: tag.Name)
	for tag in tags:
		if not tag.isReferenced():
			tag.delete()
			if deletedTagsMessage == "":
				deletedTagsMessage = 'Deleted the following tag(s):<br>"{}"'.format(tag.Name)
			else:
				deletedTagsMessage = '{}<br>"{}"'.format(deletedTagsMessage, tag.Name)

	db.session.commit()
	if deletedTagsMessage != "":
		alert = "alert alert-success"
		flash(deletedTagsMessage, alert)
	return redirect(request.referrer)

@elementAttributeTemplates.route("/elementAttributeTemplates/edit/<int:elementAttributeTemplateId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def editElementAttributeTemplate(elementAttributeTemplateId):
	operation = "Edit"
	elementAttributeTemplate = ElementAttributeTemplate.query.get_or_404(elementAttributeTemplateId)
	form = ElementAttributeTemplateForm(obj = elementAttributeTemplate)

	if elementAttributeTemplate.LookupId:
		modelName = "Lookup Element Attribute Template"
		del form.unitOfMeasurement
	else:
		modelName = "Element Attribute Template"
		del form.lookup

	# Edit an existing elementAttributeTemplate.
	if form.validate_on_submit():
		oldElementAttributeTemplateName = elementAttributeTemplate.Name
		elementAttributeTemplate.Description = form.description.data
		elementAttributeTemplate.ElementTemplateId = form.elementTemplateId.data
		elementAttributeTemplate.Name = form.name.data

		if elementAttributeTemplate.LookupId:
			elementAttributeTemplate.Lookup = form.lookup.data
		else:
			elementAttributeTemplate.UnitOfMeasurement = form.unitOfMeasurement.data

		db.session.commit()
		flash('You have successfully edited the element attribute template "{}".'.format(elementAttributeTemplate.Name), "alert alert-success")
		createdTags = []
		updatedTags = []
		createdElementAttributes = []
		updatedElementAttributes = []
		for element in elementAttributeTemplate.ElementTemplate.Elements:
			if element.isManaged():
				# Tag management.
				newTagName = "{}_{}".format(element.Name, elementAttributeTemplate.Name.replace(" ", ""))
				newTag = Tag.query.filter_by(AreaId = element.TagAreaId, Name = newTagName).one_or_none()
				oldTagName = "{}_{}".format(element.Name, oldElementAttributeTemplateName.replace(" ", ""))
				oldTag = Tag.query.filter_by(AreaId = element.TagAreaId, Name = oldTagName).one_or_none()
				if newTag is None and oldTag is None:
					# New tag doesn't exist, so create it.
					tag = Tag(AreaId = element.TagAreaId, LookupId = elementAttributeTemplate.LookupId, Name = newTagName,
						UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId)
					db.session.add(tag)
					db.session.commit()
					createdTags.append(tag)
					elementAttributeTagId = tag.TagId
				elif newTag is not None:
					# New tag exists, so update LookupId and UnitOfMeasurementId just in case.
					newTag.LookupId = elementAttributeTemplate.LookupId
					newTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					db.session.commit()
					updatedTags.append(newTag)
					elementAttributeTagId = newTag.TagId
				elif oldTag is not None:
					# Old tag exists, so update LookupId, Name and UnitOfMeasurementId just in case.
					oldTag.LookupId = elementAttributeTemplate.LookupId
					oldTag.Name = newTagName
					oldTag.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					db.session.commit()
					updatedTags.append(oldTag)
					elementAttributeTagId = oldTag.TagId

				# Element attribute management.
				elementAttribute = ElementAttribute.query.filter_by(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId,
					ElementId = element.ElementId).one_or_none()
				if elementAttribute is None:
					# The element attribute doesn't exist, so create it.
					elementAttribute = ElementAttribute(ElementAttributeTemplateId = elementAttributeTemplate.ElementAttributeTemplateId, 
						ElementId = element.ElementId, TagId = elementAttributeTagId)
					db.session.add(elementAttribute)
					db.session.commit()
					createdElementAttributes.append(elementAttribute)
				else:
					# The element attribute exists, so update TagId just in case.
					elementAttribute.TagId = elementAttributeTagId
					db.session.commit()
					updatedElementAttributes.append(elementAttribute)

		createdTagsMessage = ""
		alert = "alert alert-success"
		if createdTags:
			createdTags.sort(key = lambda tag: tag.Name)
			for tag in createdTags:
				if createdTagsMessage == "":
					createdTagsMessage = 'Created the following tag(s):<br>"{}"'.format(tag.Name)
					alert = "alert alert-success"
				else:
					createdTagsMessage = '{}<br>"{}"'.format(createdTagsMessage, tag.Name)

			flash(createdTagsMessage, alert)

		updatedTagsMessage = ""
		if updatedTags:
			updatedTags.sort(key = lambda tag: tag.Name)
			for tag in updatedTags:
				if updatedTagsMessage == "":
					updatedTagsMessage = 'Updated the following existing tag(s), if needed:<br>"{}"'.format(tag.Name)
					alert = "alert alert-warning"
				else:
					updatedTagsMessage = '{}<br>"{}"'.format(updatedTagsMessage, tag.Name)

			flash(updatedTagsMessage, alert)

		createdElementAttributesMessage = ""
		if createdElementAttributes:
			createdElementAttributes.sort(key = lambda elementAttribute: elementAttribute.Element.Name)
			for elementAttribute in createdElementAttributes:
				if createdElementAttributesMessage == "":
					createdElementAttributesMessage = "Created the following element attribute(s):<br>Element: " + \
						'"{}" attribute: "{}" associated with tag: "{}"'.format(elementAttribute.Element.Name, elementAttribute.ElementAttributeTemplate.Name,
						elementAttribute.Tag.Name)
					alert = "alert alert-success"
				else:
					createdElementAttributesMessage = '{}<br>Element: "{}" attribute: "{}" associated with tag: "{}"'.format(createdElementAttributesMessage,
						elementAttribute.Element.Name, elementAttribute.ElementAttributeTemplate.Name, elementAttribute.Tag.Name)

			flash(createdElementAttributesMessage, alert)

		updatedElementAttributesMessage = ""
		if updatedElementAttributes:
			updatedElementAttributes.sort(key = lambda elementAttribute: elementAttribute.Element.Name)
			for elementAttribute in updatedElementAttributes:
				if updatedElementAttributesMessage == "":
					updatedElementAttributesMessage = "Updated the following element attribute(s), if needed:<br>Element: " + \
						'"{}" attribute: "{}" associated with tag: "{}"'.format(elementAttribute.Element.Name, elementAttribute.ElementAttributeTemplate.Name,
						elementAttribute.Tag.Name)
					alert = "alert alert-warning"
				else:
					updatedElementAttributesMessage = '{}<br>Element: "{}" attribute: "{}" associated with tag: "{}"'.format(updatedElementAttributesMessage,
						elementAttribute.Element.Name, elementAttribute.ElementAttributeTemplate.Name, elementAttribute.Tag.Name)

			flash(updatedElementAttributesMessage, alert)

		# Event frame attribute template management.
		# Loop through event frame template hierarchies checking for an event frame attribute template with the same event frame attribute template name.
		updatedEventFrameAttributeTemplates = []
		for topLevelEventFrameTemplate in elementAttributeTemplate.ElementTemplate.EventFrameTemplates:
			for eventFrameTemplate in topLevelEventFrameTemplate.descendants([], 0):
				newEventFrameAttributeTemplate = EventFrameAttributeTemplate.query. \
					filter_by(EventFrameTemplateId = eventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId,
					Name = elementAttributeTemplate.Name).one_or_none()
				oldEventFrameAttributeTemplate = EventFrameAttributeTemplate.query. \
					filter_by(EventFrameTemplateId = eventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId,
					Name = oldElementAttributeTemplateName).one_or_none()
				if newEventFrameAttributeTemplate is not None:
					# New event frame attribute template exists, so update LookupId and UnitOfMeasurementId just in case.
					newEventFrameAttributeTemplate.LookupId = elementAttributeTemplate.LookupId
					newEventFrameAttributeTemplate.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					db.session.commit()
					updatedEventFrameAttributeTemplates.append(newEventFrameAttributeTemplate)
				elif oldEventFrameAttributeTemplate is not None:
					# Old event frame attribute template exists, so update LookupId, Name and UnitOfMeasurementId just in case.
					oldEventFrameAttributeTemplate.LookupId = elementAttributeTemplate.LookupId
					oldEventFrameAttributeTemplate.Name = elementAttributeTemplate.Name
					oldEventFrameAttributeTemplate.UnitOfMeasurementId = elementAttributeTemplate.UnitOfMeasurementId
					db.session.commit()
					updatedEventFrameAttributeTemplates.append(oldEventFrameAttributeTemplate)

		db.session.commit()

		updatedEventFrameAttributeTemplatesMessage = ""
		if updatedEventFrameAttributeTemplates:
			updatedEventFrameAttributeTemplates.sort(key = lambda eventFrameAttributeTemplate: eventFrameAttributeTemplate.path())
			for eventFrameAttributeTemplate in updatedEventFrameAttributeTemplates:
				if updatedEventFrameAttributeTemplatesMessage == "":
					updatedEventFrameAttributeTemplatesMessage = "Updated the following event frame attribute templates(s), if needed:<br>" + \
						'"{}\{}"'.format(eventFrameAttributeTemplate.path(), eventFrameAttributeTemplate.Name)
					alert = "alert alert-warning"
				else:
					updatedEventFrameAttributeTemplatesMessage = '{}<br>"{}\{}"'. \
						format(updatedEventFrameAttributeTemplatesMessage, eventFrameAttributeTemplate.path(), eventFrameAttributeTemplate.Name)

			flash(updatedEventFrameAttributeTemplatesMessage, alert)

		return redirect(form.requestReferrer.data)

	# Present a form to edit an existing elementAttributeTemplate.
	form.elementAttributeTemplateId.data = elementAttributeTemplate.ElementAttributeTemplateId
	form.description.data = elementAttributeTemplate.Description
	form.elementTemplateId.data = elementAttributeTemplate.ElementTemplateId
	form.name.data = elementAttributeTemplate.Name
	if elementAttributeTemplate.LookupId:
		form.lookup.data = elementAttributeTemplate.Lookup
	else:
		form.unitOfMeasurement.data = elementAttributeTemplate.UnitOfMeasurement

	if form.requestReferrer.data is None:
		form.requestReferrer.data = request.referrer

	breadcrumbs = [{"url" : url_for("elements.selectElement", selectedClass = "Root"),"text" : "<span class = \"glyphicon glyphicon-home\"></span>"},
		{"url" : url_for("elements.selectElement", selectedClass = "Enterprise",
			selectedId = elementAttributeTemplate.ElementTemplate.Site.Enterprise.EnterpriseId),
			"text" : elementAttributeTemplate.ElementTemplate.Site.Enterprise.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "Site", selectedId = elementAttributeTemplate.ElementTemplate.Site.SiteId),
			"text" : elementAttributeTemplate.ElementTemplate.Site.Name},
		{"url" : url_for("elements.selectElement", selectedClass = "ElementAttributeTemplate",
			selectedId = elementAttributeTemplate.ElementTemplate.ElementTemplateId),
			"text" : elementAttributeTemplate.ElementTemplate.Name},
		{"url" : None, "text" : elementAttributeTemplate.Name}]
	return render_template("addEdit.html", breadcrumbs = breadcrumbs, form = form, modelName = modelName, operation = operation)
