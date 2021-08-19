from peewee import DoesNotExist
from dateutil import parser

from app.models.event import Event
from app.models.facilitator import Facilitator
from app.models.program import Program
from app.models.term import Term
from app.models.programEvent import ProgramEvent

def getEvents(program_id=None):

    if program_id:
        Program.get_by_id(program_id) # raises an exception if program doesn't exist
        return (Event.select(Event).join(ProgramEvent)
                     .where(ProgramEvent.program == program_id).distinct())
    else:
        return Event.select()

def deleteEvent(program, eventId):

    event = Event.get_or_none(Event.id == eventId)
    if event:
        deleteEvent = event
        deleteEvent.delete_instance(recursive = True, delete_nullable = True)

def groupEventsByProgram(eventQuery):
    programs = {}

    for event in eventQuery.objects():
        programs.setdefault(Program.get_by_id(event.program_id), []).append(event)

    return programs

def groupEventsByCategory(term):

    term = Term.get_by_id(term)

    studentLedEvents = (Event.select(Event, Program.id.alias("program_id"))
                             .join(ProgramEvent)
                             .join(Program)
                             .where(Program.isStudentLed,
                                    Event.term == term))

    trainingEvents = (Event.select(Event, Program.id.alias("program_id"))
                           .join(ProgramEvent)
                           .join(Program)
                           .where(Event.isTraining,
                                  Event.term == term))


    bonnerScholarsEvents = (Event.select(Event, Program.id.alias("program_id"))
                                 .join(ProgramEvent)
                                 .join(Program)
                                 .where(Program.isBonnerScholars,
                                        Event.term == term))

    oneTimeEvents = (Event.select(Event, Program.id.alias("program_id"))
                          .join(ProgramEvent)
                          .join(Program)
                          .where(Program.isStudentLed == False,
                                 Event.isTraining == False,
                                 Program.isBonnerScholars == False,
                                 Event.term == term))

    categorizedEvents = {"Student Led Events" : groupEventsByProgram(studentLedEvents),
                         "Trainings" : groupEventsByProgram(trainingEvents),
                         "Bonner Scholars" : groupEventsByProgram(bonnerScholarsEvents),
                         "One Time Events" : groupEventsByProgram(oneTimeEvents)}
    return categorizedEvents

def eventEdit(newEventData):

    if newEventData['valid'] == True:

        eventId = newEventData['eventId']
        eventData = {
                "id": eventId,
                "term": newEventData['eventTerm'],
                "eventName": newEventData['eventName'],
                "description": newEventData['eventDescription'],
                "timeStart": newEventData['eventStartTime'],
                "timeEnd": newEventData['eventEndTime'],
                "location": newEventData['eventLocation'],
                "isRecurring": newEventData['eventIsRecurring'],
                "isTraining": newEventData['eventIsTraining'],
                "isRsvpRequired": newEventData['eventRSVP'],
                "isService": newEventData['eventServiceHours'],
                "startDate": parser.parse(newEventData['eventStartDate']),
                "endDate": parser.parse(newEventData['eventEndDate'])
            }
        eventEntry = Event.update(**eventData).where(Event.id == eventId).execute()

        if Facilitator.get_or_none(Facilitator.event == eventId):
            updateFacilitator = (Facilitator.update(user = newEventData['eventFacilitator'])
                                            .where(Facilitator.event == eventId)).execute()

        else:
            facilitatorEntry = Facilitator.create(user = newEventData['eventFacilitator'],
                                                      event = eventId)

    else:
        raise Exception("Invalid Data")
