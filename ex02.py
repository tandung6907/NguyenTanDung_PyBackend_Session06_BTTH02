from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

app = FastAPI()

students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18},
]

next_id = 4

class StudentRequest(BaseModel):
    code: str
    name: str
    email: EmailStr
    age: int = Field(gt=0)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("name không được rỗng")
        return v.strip()

    @field_validator("code")
    @classmethod
    def code_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("code không được rỗng")
        return v.strip().upper()


def find_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student
    return None


def is_code_taken(code: str, exclude_id: int = None) -> bool:
    for student in students:
        if student["code"] == code and student["id"] != exclude_id:
            return True
    return False


@app.post("/students", status_code=201)
def create_student(body: StudentRequest):
    global next_id
    if is_code_taken(body.code):
        raise HTTPException(status_code=409, detail=f"Code '{body.code}' đã tồn tại")
    new_student = {
        "id": next_id,
        "code": body.code,
        "name": body.name,
        "email": body.email,
        "age": body.age,
    }
    students.append(new_student)
    next_id += 1
    return new_student


@app.get("/students")
def get_students(
    keyword: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
):
    result = students[:]

    if keyword:
        kw = keyword.lower()
        result = [
            s for s in result
            if kw in s["name"].lower() or kw in s["code"].lower() or kw in s["email"].lower()
        ]

    if min_age is not None:
        result = [s for s in result if s["age"] >= min_age]

    if max_age is not None:
        result = [s for s in result if s["age"] <= max_age]

    return result


@app.get("/students/{student_id}")
def get_student(student_id: int):
    student = find_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}")
def update_student(student_id: int, body: StudentRequest):
    student = find_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if is_code_taken(body.code, exclude_id=student_id):
        raise HTTPException(status_code=409, detail=f"Code '{body.code}' đã tồn tại")
    student["code"] = body.code
    student["name"] = body.name
    student["email"] = body.email
    student["age"] = body.age
    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    student = find_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    students.remove(student)
    return {"message": f"Đã xóa học viên id={student_id}"}