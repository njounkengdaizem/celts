from flask import Flask, redirect, flash, url_for, request, render_template, g, json
from app.models.event import Event
from app.models.user import User
from app.models.programEvent import ProgramEvent
from app.controllers.events import events_bp
from app.logic.participants import sendUserData
from datetime import datetime

@events_bp.route('/<eventid>/kiosk', methods=['GET'])
def loadKiosk(eventid):
    """Renders kiosk for specified event."""
    event = Event.get_by_id(eventid)
    return render_template("/events/eventKiosk.html",
                            event = event,
                            eventid = eventid)

@events_bp.route('/signintoEvent', methods=['POST'])
def signinEvent():
    """Utilizes form data and sign in function. Returns correct flasher message."""
    eventid = request.form["eventid"]
    bnumber = request.form["bNumber"]
    programid = ProgramEvent.select(ProgramEvent.program).where(ProgramEvent.event == eventid)
    if len(bnumber) > 20:
        bnumber = "B"+ bnumber[1:9]
    try:
        kioskUser, userStatus = sendUserData(bnumber, eventid, programid)
        if userStatus == "banned":
            return "", 500

        elif userStatus == "already in":
            flasherMessage = f"{kioskUser.firstName} {kioskUser.lastName} Already Signed In!"
            return flasherMessage

        else:
            flasherMessage = f"{kioskUser.firstName} {kioskUser.lastName} Successfully Signed In!"
            return flasherMessage

    except Exception as e:
        print("Error in Main Page", e)
        return "", 500
