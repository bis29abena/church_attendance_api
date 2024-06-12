from enum import Enum


class ErrorMessage(Enum):
    InvalidEmail = "Email Address is not in the correct format"
    EmailNotFound = "Email Address not found"
    PasswordNotFound = "Password is incorrect"
    NoTitleFound = "No titles was found"
    TitleNotFound = "Title was not found"
    TitleNotAdded = "Title was not added"
    TileNotUpdate = "Title was not updated"
    NoEntry = "No data was found"
    UserNotAdded = "User was not created"
    UserNotFound = "User was not found"
    NoAttendanceFound = "AttendanceType was not found"
    AttendaceTypeNotAdded = "Attendance Type was not Added"
    AttendaceTypeAlreadyExist = "The Attendance Type name already exist."
    AttendanceTypeNotUpdated = "AttendanceType was not updated"
    ServiceTypeExists = "Service Type already exist"
    ServiceTypeNotAdded = "Service Type was not added"
    ServiceNotAdded = "Service was not added"
    MemberNotAdded = "Member was not added"


class SuccessMessage(Enum):
    OperationSuccessful = "Operation Successful"
    TitleAdded = "Title Added Successfully"
    TitleRemoved = "Title Removed Successfully"
    UserFound = "User Found"
    UserUpdated = "User updated/changed Successfully"
    UserRemoved = "User has been deleted"
    UserDisabled = "User Disabled Successfully"
    UserEnabled = "User Enabled Successfully"
    UserResetPassword = "User Password has been reset successfully"
    AttendanceTypeAdded = "Attendance Type was added succesfully"
    AttendanceTypeRemoved = "Attendance Type removed successfully"
    ServiceAdded = "Service Added Successfully"
    MemberAdded = "Member Added Successfully"
    
