#!/usr/bin/env python
from models.homework import Homework
from config import db
from werkzeug.exceptions import NotFound
from flask_sqlalchemy import SQLAlchemy
from helper.StrToBool import Str2bool
from helper.NullStrToNull import NullStrToNull
import services.student_service as student_service
from helper.PythonCodeChecker import PythonCodeChecker
import ast


def get():
    '''
    Get all entities
    :returns: all entity
    '''
    with db.engine.connect() as con:
        rs = con.execute("SELECT * FROM homework_system.homework")
        d, a = {}, []
        for r in rs:
            for column, value in r.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
        return a

    raise NotFound('authenticated faild for: ' + str(id))


def getAllByStudentId(id):
    with db.engine.connect() as con:
        rs = con.execute("SELECT * FROM homework_system.homework WHERE StudentId=" +
                         str(id))
        d, a = {}, []
        for r in rs:
            for column, value in r.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
        return a

    raise NotFound('authenticated faild for: ' + str(id))


def getFileByHomeworkId(id):
    return Homework.query.filter_by(id=id).first()


def post(name, classId, studentId, date):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    body = {
        "name": name,
        "classId": classId,
        "studentId": studentId,
        "date": date,
    }
    homework = Homework(**body)
    db.session.add(homework)
    db.session.commit()
    return homework


def postByListOfStudentsIds(name, classId, studentIdsList, date, argsType, examId):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    for id in studentIdsList:
        body = {
            "name": name,
            "classId": classId,
            "studentId": id,
            "date": date,
            "argsType": argsType,
            "examId": examId
        }
        homework = Homework(**body)
        db.session.add(homework)

    db.session.commit()
    return homework


def postNewExam(name, classId, isExam, studentId, examQuestion, examSolution, date, argsType):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    contentOfExamSolution = examSolution.read()

    if(argsType == 'INT'):
        examSolutionOutput = PythonCodeChecker.int(contentOfExamSolution)
    elif(argsType == 'FLOAT'):
        pass

    body = {
        "name": name,
        "classId": str(classId),
        "isExam": Str2bool.default(isExam),
        "studentId": studentId,
        "examQuestion": examQuestion.read(),
        "examSolution": contentOfExamSolution,
        "examSolutionOutput": str(examSolutionOutput),
        "argsType": argsType
    }
    homework = Homework(**body)
    db.session.add(homework)
    db.session.flush()

    hId = homework.id

    db.session.commit()

    studentsList = student_service.getStudentsListByClassId(classId)

    postByListOfStudentsIds(name, classId, studentsList, date, argsType, hId)

    return hId


def put(id, file, name, classId, status, grade, studentId, isFileExist, argsType, isExam, examId):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    body = {
        "id": id,
        "fileData": file.read(),
        "name": name,
        "classId": classId,
        "status": status,
        "grade": NullStrToNull.default(grade),
        "studentId": studentId,
        "isFileExist": Str2bool.default(isFileExist),
        "argsType": argsType,
        "isExam": Str2bool.default(isExam),
        "examId": examId
    }
    homework = Homework.query.filter_by(id=id).first()
    if homework:
        homework = Homework(**body)
        db.session.merge(homework)
        db.session.flush()
        db.session.commit()
        return homework
    raise NotFound('no such entity found with id=' + str(id))


def putWithoutFile(id,  name, classId, status, grade, studentId, argsType, isExam, examId):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    print(studentId)
    
    body = {
        "id": id,
        "name": name,
        "classId": classId,
        "status": status,
        "grade": grade,
        "studentId": studentId,
        "argsType": argsType,
        "isExam": Str2bool.default(isExam),
        "examId": examId
    }
    homework = Homework.query.filter_by(id=id).first()
    if homework:
        homework = Homework(**body)
        db.session.merge(homework)
        db.session.flush()
        db.session.commit()
        return homework
    raise NotFound('no such entity found with id=' + str(body['id']))
    
    # body = {
    #     "id": id,
    #     "name": name,
    #     "classId": classId,
    #     "status": status,
    #     "grade": grade,
    #     "studentId": studentId,
    #     "argsType": argsType,
    #     "isExam": Str2bool.default(isExam),
    #     "examId": examId
    # }
    # homework = Homework.query.get(id)
    # if homework:
    #     homework = Homework(**body)
    #     db.session.merge(homework)
    #     db.session.flush()
    #     db.session.commit()
    #     return homework
    # raise NotFound('no such entity found with id=' + str(body['id']))


def PostPythonCodeChecker(file):
    examSolutionOutput = PythonCodeChecker.int(file.read())

    return examSolutionOutput


def pythonCodeCheckerByHomeworkId(id):
    homerowk = Homework.query.filter_by(id=id).first()
    examId = homerowk.examId
    print(examId)
    
    exam = Homework.query.filter_by(id=examId).first()
    examSolutionDicStr = exam.examSolutionOutput
    
    print(exam.examSolution)
    print(homerowk.fileData)
    
    # convert string dic to dic object
    examSolutionDic = ast.literal_eval(examSolutionDicStr)

    examSolutionOutput = PythonCodeChecker.int(homerowk.fileData)
    
    grade = PythonCodeChecker.compareTwoDicsAsGrade(examSolutionDic, examSolutionOutput)
    
    print(examSolutionDic)
    print(examSolutionOutput)
    print(grade)
    
    return grade


def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    homework = Homework.query.get(id)
    if homework:
        db.session.delete(homework)
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))
