function teacherLogin() {
    window.location.href = "teacher-login.html";
}

function studentLogin() {
    alert("Student Login will be available soon.");
}

function goBack() {
    window.location.href = "index.html";
}

document.addEventListener("DOMContentLoaded", function () {

    const teacherForm = document.getElementById("teacherLoginForm");

    if (teacherForm) {

        teacherForm.addEventListener("submit", function (event) {

            event.preventDefault();

            const email = document.getElementById("teacherEmail").value;
            const password = document.getElementById("teacherPassword").value;

            if (email === "teacher@gmail.com" && password === "12345") {

                alert("Login Successful!");

                window.location.href = "teacher-dashboard.html";

            } else {

                alert("Invalid email or password.");

            }

        });

    }

});
function openQRGenerator(){
    window.HTMLOptionsCollection.href ="generator-qr.html"
}
function studentLogin(){
    windowlocatio.href="Student-LOgin.html";
}
const studentform=
document.getElementById("StudentLognForm");
if(studentForm){
    studentForm.addEventListener("submit",function(event){
        event.preventDefault();
     const studentId= document.getElementById("studentId").value;
     const password=document.getElementById("studentPassword").value;
     if(studentId === "STU001"&& password === "12345"){
        alert("student Login Successful!");
        window.location.href = "Student-dashboard.html";
     }else{
        alert("Invalid Student ID or Password.");
     }
    });
}

function openScanner() {
    window.location.href = "scan-qr.html";
}

function viewAttendance() {
    alert("My Attendance will be available soon.");
}

function studentLogout() {
    window.location.href = "index.html";
}

function teacherLogin() {
    window.location.href = "teacher-login.html";
}

function studentLogin() {
    window.location.href = "student-login.html";
}

function goBack() {
    window.location.href = "index.html";
}


// Student Login
conststudentform = document.getElementById("studentLoginForm");

if (studentForm) {

    studentForm.addEventListener("submit", function(event) {

        event.preventDefault();

        const studentId = document.getElementById("studentId").value;
        const password = document.getElementById("studentPassword").value;

        if (studentId === "STU001" && password === "12345") {

            alert("Student Login Successful!");

            window.location.href = "student-dashboard.html";

        } else {

            alert("Invalid Student ID or Password.");

        }

    });
}

  function openScanner() {
    window.location.href = "scan-qr.html";
}

function viewAttendance() {
    alert("My Attendance will be available soon.");
}

function studentLogout() {
    window.location.href = "index.html";
}

function teacherLogin() {
    window.location.href = "teacher-login.html";
}

function studentLogin() {
    window.location.href = "student-login.html";
}

function goBack() {
    window.location.href = "index.html";
}


// Student Login
const studentForm = document.getElementById("studentLoginForm");

if (studentForm) {

    studentForm.addEventListener("submit", function(event) {

        event.preventDefault();

        const studentId = document.getElementById("studentId").value;
        const password = document.getElementById("studentPassword").value;

        if (studentId === "STU001" && password === "12345") {

            alert("Student Login Successful!");

            window.location.href = "student-dashboard.html";

        } else {

            alert("Invalid Student ID or Password.");

        }

    });
}


// Student Dashboard
function openScanner() {
    window.location.href = "scan-qr.html";
}

function viewAttendance() {
    alert("My Attendance will be available soon.");
}

function studentLogout() {
    window.location.href = "index.html";
}