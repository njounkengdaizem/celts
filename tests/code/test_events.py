import pytest
from flask import g
from app import app
from peewee import DoesNotExist, OperationalError, IntegrityError
from datetime import datetime
from dateutil import parser
from werkzeug.datastructures import MultiDict

from app.models import mainDB
from app.models.event import Event
from app.models.user import User
from app.models.eventTemplate import EventTemplate
from app.models.program import Program
from app.models.programEvent import ProgramEvent
from app.models.term import Term
from app.models.interest import Interest
from app.models.eventRsvp import EventRsvp
from app.logic.events import *
from app.logic.volunteers import addVolunteerToEventRsvp
from app.logic.users import addUserInterest, removeUserInterest

@pytest.mark.integration
def test_event_model():

    # single program
    event = Event.get_by_id(12)
    assert event.singleProgram == Program.get_by_id(3)

    # no program
    event = Event.get_by_id(13)
    assert event.singleProgram == None
    assert event.noProgram

    # multi program
    event = Event.get_by_id(14)
    assert event.singleProgram == None
    assert not event.noProgram

    # program/event passed
    event = Event.get_by_id(11)
    assert event.isPast

@pytest.mark.integration
def test_getAllEvents():

    # No program is given, get all events
    events = getEvents()


    assert len(events) > 0

    assert events[0].description == "Empty Bowls Spring 2021"
    assert events[1].description == "Will donate Food to Community"
    assert events[2].description == "Lecture on adoption"

@pytest.mark.integration
def test_getEventsWithProgram():

    # Single program
    events = getEvents(program_id=2)


    assert len(events) > 0
    assert events[0].description == "Berea Buddies First Meetup"

@pytest.mark.integration
def test_getEventsInvalidProgram():

    # Invalid program
    with pytest.raises(DoesNotExist):
        getEvents(program_id= "asdf")

@pytest.mark.integration
def test_eventTemplate_model():

    template = EventTemplate(name="test", templateJSON='{"first entry":["number one", "number two"]}')
    assert template.templateData == {"first entry": ["number one", "number two"]}

    template.templateData = ["just", "an", "array"]
    template.save()

    template = EventTemplate.get(name="test")
    assert template.templateData == ["just", "an", "array"]

    template.delete_instance()

@pytest.mark.integration
def test_eventTemplate_fetch():

    template = EventTemplate(name="test2")
    template.templateData = {
                "first entry": "number one",
                "second entry": "number two",
                "fourth entry": "number four"
            }
    assert "number one" == template.fetch("first entry")
    assert "number one" == template.fetch("first entry", "1")

    assert None == template.fetch("third entry")
    assert "3" == template.fetch("third entry", "3")

    template.save()
    template.delete_instance()

@pytest.mark.integration
def test_preprocessEventData_checkboxes():

    # test that there is a return
    assert preprocessEventData({})

    # tets for return type
    assert type(preprocessEventData({}))== type({})

    # test for no keys
    eventData = {}
    newData = preprocessEventData(eventData)
    assert newData['isRsvpRequired'] == False
    assert newData['isService'] == False
    assert newData['isTraining'] == False

    eventData = {'isRsvpRequired':'', 'isRecurring': 'on', 'isService':True }
    newData = preprocessEventData(eventData)
    assert newData['isTraining'] == False
    assert newData['isRsvpRequired'] == False
    assert newData['isService'] == True
    assert newData['isRecurring'] == True

@pytest.mark.integration
def test_preprocessEventData_dates():

    eventData = {'startDate':''}
    newData = preprocessEventData(eventData)
    assert newData['startDate'] == ''
    assert newData['endDate'] == ''

    eventData = {'startDate':'09/07/21', 'endDate': '2021-08-08', 'isRecurring': 'on'}
    newData = preprocessEventData(eventData)
    assert newData['startDate'] == datetime.datetime.strptime("2021-09-07","%Y-%m-%d")
    assert newData['endDate'] == datetime.datetime.strptime("2021-08-08","%Y-%m-%d")

    # test different date formats
    eventData = {'startDate':parser.parse('09/07/21'), 'endDate': 75, 'isRecurring': 'on'}
    newData = preprocessEventData(eventData)
    assert newData['startDate'] == datetime.datetime.strptime("2021-09-07","%Y-%m-%d")
    assert newData['endDate'] == ''

    # endDate should match startDate for non-recurring events
    eventData = {'startDate':'09/07/21', 'endDate': '2021-08-08'}
    newData = preprocessEventData(eventData)
    assert newData['startDate'] == newData['endDate']

    eventData = {'startDate':'09/07/21', 'endDate': '2021-08-08', 'isRecurring': 'on'}
    newData = preprocessEventData(eventData)
    assert newData['startDate'] != newData['endDate']

@pytest.mark.integration
def test_preprocessEventData_term():

    eventData = {}
    preprocessEventData(eventData)
    assert 'term' not in eventData

    eventData = {'term': 5}
    preprocessEventData(eventData)
    assert eventData['term'] == Term.get_by_id(5)

    eventData = {'term': 'asdf'}
    preprocessEventData(eventData)
    assert eventData['term'] == ''

@pytest.mark.integration
def test_correctValidateNewEventData():

    eventData =  {'isRsvpRequired':False, 'isService':False,
                  'isTraining':True, 'isRecurring':False, 'startDate': parser.parse('1999-12-12'),
                  'endDate':parser.parse('2022-06-12'), 'programId':1, 'location':"a big room",
                  'timeEnd':'04:00', 'timeStart':'06:00', 'description':"Empty Bowls Spring 2021",
                  'name':'Empty Bowls Spring Event 1','term':1,'contactName':"Kaidou of the Beast", 'contactEmail': 'beastpirates@gmail.com'}

    isValid, eventErrorMessage = validateNewEventData(eventData)
    assert isValid == True
    assert eventErrorMessage == "All inputs are valid."

@pytest.mark.integration
def test_wrongValidateNewEventData():

    eventData =  {'isRsvpRequired':False, 'isService':False,
                  'isTraining':True, 'isRecurring':False, 'programId':1, 'location':"a big room",
                  'timeEnd':'12:00', 'timeStart':'15:00', 'description':"Empty Bowls Spring 2021",
                  'name':'Empty Bowls Spring Event 1','term':1,'contactName':"Big Mom", 'contactEmail': 'weeeDDDINgCAKKe@gmail.com'}

    eventData['isRecurring'] = True
    eventData['startDate'] = parser.parse('2021-12-12')
    eventData['endDate'] = parser.parse('2021-06-12')
    isValid, eventErrorMessage = validateNewEventData(eventData)
    assert isValid == False
    assert eventErrorMessage == "Event start date is after event end date"

    # testing checks for raw form data
    eventData["startDate"] = parser.parse('2021-10-12')
    eventData['endDate'] = parser.parse('2022-06-12')
    for boolKey in ['isRsvpRequired', 'isTraining', 'isService', 'isRecurring']:
        eventData[boolKey] = 'on'
        isValid, eventErrorMessage = validateNewEventData(eventData)
        assert isValid == False
        assert eventErrorMessage == "Raw form data passed to validate method. Preprocess first."
        eventData[boolKey] = False

    eventData['isRecurring'] = True # needed to pass the event check

    # testing event starts after it ends.
    eventData["startDate"] = parser.parse('2021-06-12')
    eventData["endDate"] = parser.parse('2021-06-12')
    eventData["timeStart"] =  '21:39'
    isValid, eventErrorMessage = validateNewEventData(eventData)
    assert isValid == False
    assert eventErrorMessage == "Event start time is after event end time"

    # testing same event already exists if no event id
    eventData["startDate"] = parser.parse('2021-10-12')
    eventData['endDate'] = parser.parse('2022-06-12')
    isValid, eventErrorMessage = validateNewEventData(eventData)
    assert isValid == False
    assert eventErrorMessage == "This event already exists"

    # If we provide an event id, don't check for existence
    eventData['id'] = 5
    isValid, eventErrorMessage = validateNewEventData(eventData)
    assert isValid

@pytest.mark.integration
def test_calculateRecurringEventFrequency():

    eventInfo = {'name':"testEvent",
                 'startDate': parser.parse("02/22/2023"),
                 'endDate': parser.parse("03/9/2023")}

    # test correct response
    returnedEvents = calculateRecurringEventFrequency(eventInfo)
    assert returnedEvents[0] == {'name': 'testEvent Week 1', 'date': parser.parse('02/22/2023'), 'week': 1}
    assert returnedEvents[1] == {'name': 'testEvent Week 2', 'date': parser.parse('03/01/2023'), 'week': 2}
    assert returnedEvents[2] == {'name': 'testEvent Week 3', 'date': parser.parse('03/08/2023'), 'week': 3}

    # test non-datetime
    eventInfo["startDate"] = '2021/06/07'
    with pytest.raises(Exception):
        returnedEvents = calculateRecurringEventFrequency(eventInfo)

    # test non-recurring
    eventInfo["startDate"] = '2021/06/07'
    eventInfo["endDate"] = '2021/06/07'
    with pytest.raises(Exception):
        returnedEvents = calculateRecurringEventFrequency(eventInfo)

@pytest.mark.integration
def test_attemptSaveEvent():
    with mainDB.atomic() as transaction2:
        # This test duplicates some of the saving tests, but with raw data, like from a form
        eventData =  {'isRsvpRequired':False, 'isService':False,
                      'isTraining':True, 'isRecurring':True, 'recurringId':0, 'startDate': '2021-12-12',
                      'endDate': '2021-06-12', 'programId':1, 'location':"a big room",
                      'timeEnd':'09:00 PM', 'timeStart':'06:00 PM', 'description':"Empty Bowls Spring 2021",
                      'name':'Empty Bowls Spring','term':1,'contactName':"Monkey D. Luffy", 'contactEmail': 'strawhats@hotmail.com'}
        eventInfo =  { 'isTraining':'on', 'isRecurring':False, 'recurringId':None, 'startDate': '2021-12-12',
                       'endDate':'2022-06-12', 'location':"a big room",
                       'timeEnd':'09:00 PM', 'timeStart':'06:00 PM', 'description':"Empty Bowls Spring 2021",
                       'name':'Attempt Save Test','term':1,'contactName':"Garrett D. Clark", 'contactEmail': 'boorclark@gmail.com'}
        eventInfo['program'] = Program.get_by_id(1)

        with mainDB.atomic() as transaction:
            with app.app_context():
                g.current_user = User.get_by_id("ramsayb2")
                success, errorMessage = attemptSaveEvent(eventInfo)
            if not success:
                pytest.fail(f"Save failed: {errorMessage}")

            try:
                event = Event.get(name="Attempt Save Test")

            except Exception as e:
                pytest.fail(str(e))

            finally:
                transaction.rollback() # undo our database changes

        transaction2.rollback()

@pytest.mark.integration
def test_saveEventToDb_create():

    eventInfo =  {'isRsvpRequired':False, 'isService':False,
                  'isTraining':True, 'isRecurring':False,'isAllVolunteerTraining': True, 'recurringId':None, 'startDate': parser.parse('2021-12-12'),
                   'endDate':parser.parse('2022-06-12'), 'location':"a big room",
                   'timeEnd':'09:00 PM', 'timeStart':'06:00 PM', 'description':"Empty Bowls Spring 2021",
                   'name':'Empty Bowls Spring','term':1,'contactName':"Finn D. Bledsoe", 'contactEmail': 'finninmanBledsoe@pigeoncarrier.com'}
    eventInfo['program'] = Program.get_by_id(1)

    # if valid is not added to the dict
    with pytest.raises(Exception):
        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            saveEventToDb(eventInfo)

    # if 'valid' is not True
    eventInfo['valid'] = False
    with pytest.raises(Exception):
        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            saveEventToDb(eventInfo)

    #test that the event is added successfully
    with mainDB.atomic() as transaction:
        eventInfo['valid'] = True
        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            createdEvents = saveEventToDb(eventInfo)
        assert len(createdEvents) == 1
        assert createdEvents[0].singleProgram.id == 1

        transaction.rollback()

@pytest.mark.integration
def test_saveEventToDb_recurring():
    with mainDB.atomic() as transaction:
        with app.app_context():

            eventInfo =  {'isRsvpRequired':False, 'isService':False, 'isAllVolunteerTraining': True,
                          'isTraining':True, 'isRecurring': True, 'recurringId':1, 'startDate': parser.parse('12-12-2021'),
                           'endDate':parser.parse('01-18-2022'), 'location':"this is only a test",
                           'timeEnd':'09:00 PM', 'timeStart':'06:00 PM', 'description':"Empty Bowls Spring 2021",
                           'name':'Empty Bowls Spring','term':1,'contactName':"Brianblius Ramsablius", 'contactEmail': 'ramsayBlius@gmail.com'}
            eventInfo['valid'] = True
            eventInfo['program'] = Program.get_by_id(1)

            g.current_user = User.get_by_id("ramsayb2")
            createdEvents = saveEventToDb(eventInfo)
            assert len(createdEvents) == 6

            transaction.rollback()

@pytest.mark.integration
def test_saveEventToDb_update():
    with mainDB.atomic() as transaction:

        eventId = 4
        beforeUpdate = Event.get_by_id(eventId)
        assert beforeUpdate.name == "First Meetup"

        newEventData = {
                        "id": 4,
                        "program": 1,
                        "term": 1,
                        "name": "First Meetup",
                        "description": "This is a Test",
                        "timeStart": "06:00 PM",
                        "timeEnd": "09:00 PM",
                        "location": "House",
                        'isRecurring': True,
                        'recurringId': 2,
                        'isTraining': True,
                        'isRsvpRequired': False,
                        'isAllVolunteerTraining': True,
                        'isService': False,
                        "startDate": "2021-12-12",
                        "endDate": "2022-6-12",
                        "contactName": "Monkey D. Luffy",
                        "contactEmail": "goatpiece@berea.edu",
                        "valid": True
                    }
        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            eventFunction = saveEventToDb(newEventData)
        afterUpdate = Event.get_by_id(newEventData['id'])
        assert afterUpdate.description == "This is a Test"
        assert afterUpdate.isAllVolunteerTraining == True

        newEventData = {
                        "id": 4,
                        "program": 1,
                        "term": 1,
                        "name": "First Meetup",
                        "description": "Berea Buddies First Meetup",
                        "timeStart": "06:00 PM",
                        "timeEnd": "09:00 PM",
                        "location": "House",
                        'isRecurring': True,
                        'recurringId': 3,
                        'isTraining': True,
                        'isRsvpRequired': False,
                        'isAllVolunteerTraining': False,
                        'isService': 5,
                        "startDate": "2021-12-12",
                        "endDate": "2022-6-12",
                        "contactName": "Monkey D. Luffy",
                        "contactEmail": "goatpiece@berea.edu",
                        "valid": True
                    }
        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            eventFunction = saveEventToDb(newEventData)
        afterUpdate = Event.get_by_id(newEventData['id'])

        assert afterUpdate.description == "Berea Buddies First Meetup"

        transaction.rollback()

@pytest.mark.integration
def test_deleteEvent():
    with mainDB.atomic() as transaction:

        testingEvent = Event.create(name = "Testing delete event",
                                      term = 2,
                                      description= "This Event is Created to be Deleted.",
                                      timeStart= "06:00 PM",
                                      timeEnd= "09:00 PM",
                                      location = "No Where",
                                      isRsvpRequired = 0,
                                      isTraining = 0,
                                      isService = 0,
                                      startDate= "2021-12-12",
                                      endDate= "2022-6-12",
                                      recurringId = None)

        testingEvent = Event.get(Event.name == "Testing delete event")

        eventId = testingEvent.id
        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            deletingEvent = deleteEvent(eventId)
        assert Event.get_or_none(Event.id == eventId) is None

        with app.app_context():
            g.current_user = User.get_by_id("ramsayb2")
            deletingEvent = deleteEvent(eventId)
        assert Event.get_or_none(Event.id == eventId) is None
        transaction.rollback()

@pytest.mark.integration
def test_upcomingEvents():
    with mainDB.atomic() as transaction:
        testDate = datetime.datetime.strptime("2021-08-01 05:00","%Y-%m-%d %H:%M")

        # Create a user to run the tests with
        user = User.create(username = 'usrtst',
                              firstName = 'Test',
                              lastName = 'User',
                              bnumber = '03522492',
                              email = 'usert@berea.deu',
                              isStudent = True)

        # Create an event that is not a part of a program the user can RSVP to
        noProgram = Event.create(name = "Upcoming event with no program",
                                term = 2,
                                description = "Test upcoming no program event.",
                                timeStart = "18:00:00",
                                timeEnd = "21:00:00",
                                location = "The moon",
                                startDate = "2021-12-12",
                                endDate = "2021-12-13")

        # Create a Program Event to show up when the user marks interest in a
        # new program
        newProgramEvent = Event.create(name = "Upcoming event with  program",
                                term = 2,
                                description = "Test upcoming program event.",
                                timeStart = "18:00:00",
                                timeEnd = "21:00:00",
                                location = "The sun",
                                startDate = "2021-12-12",
                                endDate = "2021-12-13")

        # Create a new Program to create the new Program Event off of so the
        # user can mark interest for it
        programForInterest = Program.create(id = 13,
                                            programName = "BOO",
                                            isStudentLed = False,
                                            isBonnerScholars = False,
                                            contactEmail = "test@email",
                                            contactName = "testName")

        ProgramEvent.create(program = programForInterest, event = newProgramEvent)

        # User has not RSVPd and is Interested
        addInterest = addUserInterest(programForInterest.id, user)
        eventsInUserInterestedProgram = getUpcomingEventsForUser(user, asOf = testDate)

        assert eventsInUserInterestedProgram == [newProgramEvent]

        # user has RSVPd and is Interested
        addUserRsvp = addVolunteerToEventRsvp(user, noProgram.id)
        eventsInUserInterestAndRsvp = getUpcomingEventsForUser(user, asOf = testDate)

        interestAndRsvp = [[newProgramEvent] + [noProgram]]

        assert eventsInUserInterestAndRsvp in interestAndRsvp

        # User has RSVPd and is not Interested
        removeInterest = removeUserInterest(programForInterest.id, user)
        eventsInUserRsvp = getUpcomingEventsForUser(user, asOf = testDate)

        assert eventsInUserRsvp == [noProgram]

        transaction.rollback()

@pytest.mark.integration
def test_format24HourTime():

    # tests valid "input times"
    assert format24HourTime('08:00 AM') == "08:00"
    assert format24HourTime('5:38 AM') == "05:38"
    assert format24HourTime('05:00 PM') == "17:00"
    assert format24HourTime('7:30 PM') == "19:30"
    assert format24HourTime('12:32 PM') == "12:32"
    assert format24HourTime('12:01 AM') == "00:01"
    assert format24HourTime('12:32') == "12:32"
    assert format24HourTime('00:01') == "00:01"
    assert format24HourTime('17:07') == "17:07"
    assert format24HourTime('23:59') == "23:59"
    time = datetime.datetime(1900, 1, 1, 8, 30)
    assert format24HourTime(time) == "08:30"
    time = datetime.datetime(1900, 1, 1, 23, 59)
    assert format24HourTime(time) == "23:59"
    time = datetime.datetime(1900, 1, 1, 00, 1)
    assert format24HourTime(time) == "00:01"

    # tests "input times" that are not valid inputs
    with pytest.raises(ValueError):
        assert format24HourTime('13:30 PM')
        assert format24HourTime('13:30 AM')
        assert format24HourTime(':30')
        assert format24HourTime('01:30:00 PM')
        assert format24HourTime('Clever String')

@pytest.mark.integration
def test_calculateNewrecurringId():

    maxRecurringId = Event.select(fn.MAX(Event.recurringId)).scalar()
    if maxRecurringId == None:
        maxRecurringId = 1
    else:
        maxRecurringId += 1
    assert calculateNewrecurringId() == maxRecurringId

@pytest.mark.integration
def test_getPreviousRecurringEventData():
    with mainDB.atomic() as transaction:

        testingEvent1 = Event.create(name = "Testing delete event",
                                      term = 2,
                                      description= "This Event is Created to be Deleted.",
                                      timeStart= "6:00 pm",
                                      timeEnd= "9:00 pm",
                                      location = "No Where",
                                      isRsvpRequired = 0,
                                      isTraining = 0,
                                      isService = 0,
                                      startDate= "2021-12-5",
                                      endDate= "2022-12-5",
                                      recurringId = 3)
        testingEvent2 = Event.create(name = "Testing delete event",
                                      term = 2,
                                      description= "This Event is Created to be Deleted.",
                                      timeStart= "6:00 pm",
                                      timeEnd= "9:00 pm",
                                      location = "No Where",
                                      isRsvpRequired = 0,
                                      isTraining = 0,
                                      isService = 0,
                                      startDate= "2022-12-12",
                                      endDate= "2022-12-12",
                                      recurringId = 3)
        testingEvent3 = Event.create(name = "Testing delete event",
                                      term = 2,
                                      description= "This Event is Created to be Deleted.",
                                      timeStart= "6:00 pm",
                                      timeEnd= "9:00 pm",
                                      location = "No Where",
                                      isRsvpRequired = 0,
                                      isTraining = 0,
                                      isService = 0,
                                      startDate= "2022-12-19",
                                      endDate= "2022-12-19",
                                      recurringId = 3)

        testingParticipant1 = EventParticipant.create(user = User.get_by_id("neillz"),
                                                    event = testingEvent2.id,
                                                    hoursEarned = None)
        testingParticipant2 = EventParticipant.create(user = User.get_by_id("ramsayb2"),
                                                    event = testingEvent2.id,
                                                    hoursEarned = None)
        testingParticipant3 = EventParticipant.create(user = User.get_by_id("khatts"),
                                                    event = testingEvent2.id,
                                                    hoursEarned = None)

        val = getPreviousRecurringEventData(testingEvent3.recurringId)
        assert val[0].username == "neillz"
        assert val[1].username == "ramsayb2"
        assert val[2].username == "khatts"
        transaction.rollback()
