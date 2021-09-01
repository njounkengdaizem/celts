from flask import request, render_template, g, abort, flash, redirect, url_for
from app.models.user import User
from app.models.eventParticipant import EventParticipant
from app.models.program import Program
from app.models.interest import Interest
from app.controllers.main import main_bp
from app.logic.events import getUpcomingEventsForUser
from app.logic.users import addRemoveInterest
from app.logic.participants import userRsvpForEvent, unattendedRequiredEvents

@main_bp.route('/')
def home():
    print(f"{g.current_user.username}: {g.current_user.firstName} {g.current_user.lastName}")
    return render_template('main/home.html', title="Welcome to CELTS!")

@main_bp.route('/profile/<username>', methods = ['GET'])
def profilePage(username):
    if not g.current_user.isCeltsAdmin or g.current_user.isCeltsStudentStaff or g.current_user.username == username:
        print(g.current_user.username)
        return "Access Denied", 403
    else:
        profileUser = User.select().where(User.username == username)
        upcomingEvents = getUpcomingEventsForUser(username)
        programs = Program.select()
        interests = Interest.select().where(Interest.user == g.current_user)
        interests_ids = [interest.program for interest in interests]
        return render_template('/volunteer/volunteerProfile.html',
                               title="Volunteer Interest",
                               user = profileUser,
                               programs = programs,
                               interests = interests,
                               interests_ids = interests_ids,
                               upcomingEvents = upcomingEvents)

@main_bp.route('/deleteInterest/<program_id>', methods = ['POST'])
@main_bp.route('/addInterest/<program_id>', methods = ['POST'])
def updateInterest(program_id):
    """
    This function updates the interest table by adding a new row when a user
    shows interest in a program
    """
    rule = request.url_rule
    user = g.current_user
    try:
        return addRemoveInterest(rule, program_id, user)

    except Exception as e:
        print(e)
        return "Error Updating Interest", 500

@main_bp.route('/rsvpForEvent', methods = ['POST'])
def volunteerRegister():
    """
    This function selects the user ID and event ID and registers the user
    for the event they have clicked register for.
    """
    eventData = request.form
    userId = g.current_user
    isEligible = userRsvpForEvent(userId, eventData['eventId'])
    listOfRequirements = unattendedRequiredEvents(eventData['programId'], userId)

    if not isEligible: # if they are banned
        flash(f"Cannot RSVP. Contact CELTS administrators: {app.config['celts_admin_contact']}.", "danger")

    elif listOfRequirements:
        reqListToString = ', '.join(listOfRequirements)
        flash(f"{userId.firstName} {userId.lastName} successfully registered. However, the following training may be required: {reqListToString}.", 'success')

    #if they are eligible
    else:
        flash("Successfully registered for event!","success")
    if 'from' in eventData:
        if eventData['from'] == 'ajax':
            return ''
    return redirect(url_for("admin.editEvent", eventId=eventData['eventId'], program=eventData['programId']))


@main_bp.route('/rsvpRemove', methods = ['POST'])
def RemoveRSVP():
    """
    This function deletes the user ID and event ID from database when RemoveRSVP  is clicked
    """

    eventData = request.form
    userId = User.get(User.username == g.current_user)
    eventId = eventData['eventId']
    program = eventData['programId']

    currentEventParticipant = EventParticipant.get(EventParticipant.user == userId, EventParticipant.event == eventId)

    currentEventParticipant.delete_instance()
    flash("Successfully unregistered for event!","success")
    return redirect(url_for("admin.editEvent", eventId=eventId, program=program))
