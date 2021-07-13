from dateutil import parser
from app.models.event import Event
from flask import request
from app.controllers.admin import admin_bp
from app.logic.adminNewEvent import createNewEvent, setValueForUncheckedBox
from app.logic.validateNewEvent import validateNewEventData
from flask import flash, redirect, url_for, g


@admin_bp.route('/createEvent', methods=['POST'])
def createEvent():

    if g.current_user.isCeltsAdmin:

        eventData = request.form.copy() # request.form returns a immutable dict so we need to copy to make changes
        newEventData= setValueForUncheckedBox(eventData)

        #if an event is not recurring then it wil have same end and start date
        if newEventData['eventEndDate'] == '':
            newEventData['eventEndDate'] = newEventData['eventStartDate']


        # convert date into datetime object (Y-m-d) for the backend
        newEventData['eventStartDate'] = parser.parse(newEventData['eventStartDate'], dayfirst=True)
        newEventData['eventEndDate'] = parser.parse(newEventData['eventEndDate'], dayfirst=True)


        # function to validate data
        dataIsValid, validationErrorMessage = validateNewEventData(newEventData)

        if dataIsValid:
            createNewEvent(newEventData)

            flash("Event successfully created!")
            return redirect(url_for("admin.createEventPage", program=newEventData['programId']))

        else:
            flash(validationErrorMessage)
            return redirect(url_for("admin.createEventPage", program=2)) #FIXME: have this redirect to main programs page (or some appropriate non admin page).

    flash("Only celts admins can create an event!")
    return redirect(url_for("admin.createEventPage", program=2)) #FIXME: have this redirect to main programs page (or some appropriate non admin page).
