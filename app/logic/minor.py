from app.models.user import User
from app.models.course import Course
from app.models.courseParticipant import CourseParticipant
from app.models.program import Program
from app.models.event import Event
from app.models.eventParticipant import EventParticipant
from collections import defaultdict
from playhouse.shortcuts import model_to_dict
from peewee import JOIN

def updateMinorInterest(username):
    """
    Given a username, update their minor interest and minor status.
    """
    user = User.get(username=username)
    user.minorInterest = not user.minorInterest
    if user.minorInterest == True:
        user.minorStatus = "Interested"
    else:
        user.minorStatus = "No interest"

    user.save()

def getProgramEngagementHistory(program_id, username, term):
    eventsInProgramAndTerm = (Event.select(Event.id, Event.name)
                               .join(Program, JOIN.LEFT_OUTER).switch()
                               .join(EventParticipant)
                               .where(EventParticipant.user == username,
                                      Event.term == term, Program.id == program_id)
                                      )
    participatedEvents = [model_to_dict(event) for event in eventsInProgramAndTerm]

    return participatedEvents



def getCommunityEngagementByTerm(username):
    """
    Given a username, return all of their community engagements (service learning courses and event participations.)
    """

    courses = (Course.select(Course)
                       .join(CourseParticipant, on=(Course.id == CourseParticipant.course))
                       .where(CourseParticipant.user == username)
                       .group_by(Course.courseName, Course.term))
    
    terms = defaultdict(list)
    for course in courses:
        terms[course.term.description].append({"name":course.courseName, "id":course.id, "type":"course", "term":course.term})

    events = (Event.select(Event)
                       .join(EventParticipant, on=(Event.id == EventParticipant.event))
                       .where(EventParticipant.user == username)
                       .group_by(Event.program, Event.term))
    
    for event in events:
        terms[event.term.description].append({"name":event.program.programName, "id":event.program.id, "type":"program", "term":event.term})
    
    return terms



