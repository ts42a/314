document.addEventListener("DOMContentLoaded", function () {
    // Set User Type for Sign-Up Modal
    function setUserType(type) {
        const userForm = document.getElementById("userSignUpForm");
        const organizerForm = document.getElementById("organizerSignUpForm");
        const userBtn = document.querySelector("#signupModal .btn-user");
        const organizerBtn = document.querySelector("#signupModal .btn-organizer");

        if (type === "user") {
            userForm.style.display = "block";
            organizerForm.style.display = "none";
            userBtn.classList.add("active");
            organizerBtn.classList.remove("active");
        } else {
            userForm.style.display = "none";
            organizerForm.style.display = "block";
            organizerBtn.classList.add("active");
            userBtn.classList.remove("active");
        }
    }

    // Set Sign-In Type
    function setSignInType(type) {
        const userForm = document.getElementById("userSignInForm");
        const organizerForm = document.getElementById("organizerSignInForm");
        const userBtn = document.querySelector("#signInModal .btn-user");
        const organizerBtn = document.querySelector("#signInModal .btn-organizer");

        if (type === "user") {
            userForm.style.display = "block";
            organizerForm.style.display = "none";
            userBtn.classList.add("active");
            organizerBtn.classList.remove("active");
        } else {
            userForm.style.display = "none";
            organizerForm.style.display = "block";
            organizerBtn.classList.add("active");
            userBtn.classList.remove("active");
        }
    }

    window.setUserType = setUserType;
    window.setSignInType = setSignInType;
});

// Clear error + restore signup form
function hideSignupError() {
    document.getElementById('signup-error').style.display = 'none';

    const userBtn = document.querySelector("#signupModal .btn-user");
    if (userBtn.classList.contains("active")) {
        document.getElementById("userSignUpForm").style.display = "block";
    } else {
        document.getElementById("organizerSignUpForm").style.display = "block";
    }
}

// Clear error + restore signin form
function hideSigninError() {
    document.getElementById('signin-error').style.display = 'none';

    const userBtn = document.querySelector("#signInModal .btn-user");
    if (userBtn.classList.contains("active")) {
        document.getElementById("userSignInForm").style.display = "block";
    } else {
        document.getElementById("organizerSignInForm").style.display = "block";
    }
}
