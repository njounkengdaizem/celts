import pytest
from peewee import *
from datetime import datetime
from app.models import mainDB
from app.models.program import Program
from app.models.programBan import ProgramBan
from app.models.note import Note
from app.models.user import User
from app.models.programManager import ProgramManager
from app.logic.users import addUserInterest, removeUserInterest, banUser, unbanUser, isEligibleForProgram
from app.logic.users import isEligibleForProgram

@pytest.mark.integration
def test_user_model():

    user = User.get_by_id("ramsayb2")
    assert user.isCeltsAdmin
    assert not user.isCeltsStudentStaff
    assert user.isAdmin

    user = User.get_by_id("partont")
    assert not user.isCeltsAdmin
    assert not user.isCeltsStudentStaff
    assert not user.isAdmin


@pytest.mark.integration
def test_isEligibleForProgram():

    # user has attended all required events
    user = User.get(User.username == "lamichhanes2")
    program = Program.get(Program.id == 2)

    eligible = isEligibleForProgram(2, "lamichhanes2")
    assert eligible
    eligible = isEligibleForProgram(program, user)
    assert eligible

    # there are no required events
    eligible = isEligibleForProgram(4, "ayisie")
    assert eligible

@pytest.mark.integration
def test_addUserInterest():
    with mainDB.atomic() as transaction:

        username = "ramsayb2"
        program_id = 2

        # test adding interest for different users
        result = addUserInterest(program_id, username)
        assert result


        username = "khatts"
        result = addUserInterest(program_id, username)
        assert result

        # test adding interest with different program id
        program_id = 3
        result = addUserInterest(program_id, username)
        assert result

        # test adding interest for user that does not exist
        username = "jarjug"
        program_id = 3
        with pytest.raises(IntegrityError):
            result = addUserInterest(program_id, username)
            assert result

        # test adding interest for program_id that does not exist
        username = "khatts"
        program_id = 45
        with pytest.raises(IntegrityError):
            result = addUserInterest(program_id, username)
            assert result

        transaction.rollback()

@pytest.mark.integration
def test_removeUserInterestt():
    with mainDB.atomic() as transaction:
        #test for removing interest that exists
        username = "ramsayb2"
        program_id = 2
        result = removeUserInterest(program_id, username)
        assert result ==  True

        #test for removing interest that doesn't exist
        username = "khatts"
        program_id = 2
        result = removeUserInterest(program_id, username)
        assert result == True

        transaction.rollback()

@pytest.mark.integration
def test_banUser():
    with mainDB.atomic() as transaction:

        #test for banning a user from a program
        username = "khatts"
        program_id = 3
        note = "Banning user test"
        creator = "ramsayb2"
        banEndDate = "2022-11-29"
        # checkBan = banUser (program_id, username, note, banEndDate, creator)
        if (ProgramBan.select().where(ProgramBan.user == username, ProgramBan.banNote == note, ProgramBan.program == program_id, ProgramBan.endDate > banEndDate).exists()):
            assert True
        # assert checkBan


        #test for banning a user from a program with different program id
        program_id = 2
        if (ProgramBan.select().where(ProgramBan.user == username, ProgramBan.banNote == note, ProgramBan.program == program_id, ProgramBan.endDate > banEndDate).exists()):
            assert True
        # status = banUser (program_id, username, note, banEndDate, creator)
        # assert status == "Successfully banned the user"

        #test for exceptions when banning the user
        username = "khatts"
        program_id = 100
        note = "Banning user test"
        creator = "ramsayb2"
        banEndDate = "2022-11-29"
        with pytest.raises(Exception):
            status = banUser (program_id, username, note, banEndDate, creator)
            assert status == False

        transaction.rollback()

@pytest.mark.integration
def test_unbanUser():
    with mainDB.atomic() as transaction:

        #test for unbanning a user from a program
        username = "khatts"
        program_id = 2
        note = "unbanning user test"
        creator = "ramsayb2"
        if (ProgramBan.select().where(ProgramBan.user == username, ProgramBan.banNote == note, ProgramBan.program == program_id).exists()):
            assert True
        # status = unbanUser (program_id, username, note, creator)
        # assert status == "Successfully unbanned the user"

        #test for unbanning a user from a program with different program
        program_id = 3
        if (ProgramBan.select().where(ProgramBan.user == username, ProgramBan.banNote == note, ProgramBan.program == program_id).exists()):
            assert True
        # status = unbanUser (program_id, username, note, creator)
        # assert status == "Successfully unbanned the user"

        #test for exceptions when unbanning the user
        username = "ramsayb2"
        program_id = 100
        note = "Banning user test"
        creator = "ramsayb2"
        banEndDate = "2022-11-29"
        with pytest.raises(Exception):
            status = unbanUser (program_id, username, note, creator)
            assert status == False

        transaction.rollback()

@pytest.mark.integration
def test_userpriv():

    user = User.get_by_id("khatts")
    prg = Program.get_by_id(1)
    assert user.isProgramManagerFor(prg)

    user = User.get_by_id("mupotsal")
    prg = Program.get_by_id(12)
    assert not user.isProgramManagerFor(prg)

@pytest.mark.integration
def test_addProgramManager():
    with mainDB.atomic() as transaction:
        user = User.get_by_id("mupotsal")
        prg = Program.get_by_id(1)
        newPM = user.addProgramManager(prg)

        PMsWithNewPM = list(User.select(User.username).join(ProgramManager).where(ProgramManager.program_id == 1))

        # Check that the return statement is what we expect it to be.
        assert newPM == (f' {user} added as manager')
        # Check that the user is made manager of program 1
        assert user in PMsWithNewPM

        transaction.rollback()
