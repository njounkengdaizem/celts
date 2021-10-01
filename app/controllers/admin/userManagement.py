from flask import Flask
from app.models.user import User
from app.controllers.admin import admin_bp
from app.logic.userManagement import addCeltsAdmin,addCeltsStudentStaff,removeCeltsAdmin,removeCeltsStudentStaff

@admin_bp.route('/manageUsers/<method>/<user>', methods = ['GET'])
def manageUsers(user,method):
    # we will give each method a number
    # method1 = addCeltsAdmin, 2 = addCeltsStudentStaff, 3= removeCeltsAdmin, 4 = removeCeltsStudentStaff
    user = User.get_by_id(user)
    method = int(method)
    if method == 1:
        addCeltsAdmin(user)
    elif method == 2:
        addCeltsStudentStaff(user)
    elif method == 3:
        removeCeltsAdmin(user)
    elif method == 4:
        removeCeltsStudentStaff(user)
    else:
        return {
        "There is an error":"error"
        }

    print("user........",user)
    return {
    "method":method,
    "user":user.username
    }
