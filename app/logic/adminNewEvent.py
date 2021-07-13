from app.models.event import Event
from datetime import *
# from datetime import timedelta
from app.models.facilitator import Facilitator
# from dateutil import parser

def calculateRecurringEventFrequency(recurringEventInfo):
    """
    """

    eventName = recurringEventInfo['eventName']

    endDate = datetime.strptime(recurringEventInfo['eventEndDate'], '%m/%d/%Y')
    startDate = datetime.strptime(recurringEventInfo['eventStartDate'], '%m/%d/%Y')

    recurringEvents = []

    if endDate == startDate:
        raise Exception("This event is not a recurring Event")

    if recurringEventInfo['eventFrequency'] == 'weekly':
        counter = 0
        for i in range(0, ((endDate-startDate).days +1), 7):
            counter += 1
            recurringEvents.append({'eventName': f"{eventName} week {counter}",
            'Date':startDate.strftime('%m/%d/%Y')})
            startDate += timedelta(days=7)

    elif recurringEventInfo['eventFrequency'] == "daily":
        counter = 0
        for i in range(0, ((endDate-startDate).days +1)):
            counter += 1
            recurringEvents.append({'eventName': f"{eventName} day {counter}",
            'Date':startDate.strftime('%m/%d/%Y')})
            startDate += timedelta(days=1)

    elif recurringEventInfo['eventFrequency'] == "monthly":
        counter = 0
        for i in range(0, ((endDate.month-startDate.month) +1)):
            counter += 1
            recurringEvents.append({'eventName': f"{eventName} month {counter}",
            'Date':startDate.strftime('%m/%d/%Y')})
            startDate += timedelta()

    print(recurringEvents)

def setValueForUncheckedBox(eventData):

    eventCheckBoxes = ['eventRequiredForProgram','eventRSVP', 'eventServiceHours', 'eventIsTraining', 'eventIsRecurring']

    for checkBox in eventCheckBoxes:
        if checkBox not in eventData:
            eventData[checkBox] = False

    return eventData

def createNewEvent(newEventData):

    eventEntry = Event.create(eventName = newEventData['eventName'],
                              term = newEventData['eventTerm'],
                              description= newEventData['eventDescription'],
                              timeStart = newEventData['eventStartTime'],
                              timeEnd = newEventData['eventEndTime'],
                              location = newEventData['eventLocation'],
                              isRecurring = newEventData['eventIsRecurring'],
                              isRsvpRequired = newEventData['eventRSVP'],
                              isRequiredForProgram = newEventData['eventRequiredForProgram'],
                              isTraining = newEventData['eventIsTraining'],
                              isService = newEventData['eventServiceHours'],
                              startDate =  newEventData['eventStartDate'],
                              endDate =  newEventData['eventEndDate'],
                              program = newEventData['programId'])

    facilitatorEntry = Facilitator.create(user = newEventData['eventFacilitator'],
                                          event = eventEntry )
