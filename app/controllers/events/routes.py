from flask import Flask, redirect, flash, url_for, request, render_template, g, json
from app.controllers.events import events_bp
from app.models.event import Event
from app.models.user import User
from app.models.programEvent import ProgramEvent
from app.logic.events import getEvents
from app.models.term import Term
from app.logic.events import groupEventsByCategory
from app.logic.getUpcomingEvents import getUpcomingEventsForUser
from app.logic.signinKiosk import sendUserData

@events_bp.route('/events/<term>/', methods=['GET'])
def events(term):

    print("This is the term", term)
    if not term.isdigit():
        listOfTerms = Term.select()
        for term_id in listOfTerms.objects():
            if term_id.isCurrentTerm == True:
                term = term_id
                print(term, "new term")


    eventsDict = groupEventsByCategory(term)
    listOfTerms = Term.select()
    print(list(listOfTerms), "LISTOFTERM")
    for term in listOfTerms.objects():
        print(term.id)
        print(term.isCurrentTerm)
    return render_template("/events/event_list.html",
        selectedTerm = Term.get_by_id(term),
        eventDict = eventsDict,
        listOfTerms = listOfTerms,
        user = g.current_user)


@events_bp.route('/events/upcoming_events', methods=['GET'])
def showUpcomingEvent():
    upcomingEvents = getUpcomingEventsForUser(g.current_user)
    return render_template('/events/showUpcomingEvents.html',
                            upcomingEvents = upcomingEvents)


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
