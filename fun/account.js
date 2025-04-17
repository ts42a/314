document.addEventListener("DOMContentLoaded", function () {
    // Set User Type for Sign-Up & Sign-In
    function setUserType(type) {
        const userSignUpForm = document.getElementById("userSignUpForm");
        const organizerSignUpForm = document.getElementById("organizerSignUpForm");
        const userButton = document.querySelector("#signupModal .btn-user");
        const organizerButton = document.querySelector("#signupModal .btn-organizer");

        if (type === "user") {
            userSignUpForm.style.display = "block";
            organizerSignUpForm.style.display = "none";
            userButton.classList.add("active");
            organizerButton.classList.remove("active");
        } else if (type === "organizer") {
            userSignUpForm.style.display = "none";
            organizerSignUpForm.style.display = "block";
            organizerButton.classList.add("active");
            userButton.classList.remove("active");
        }
    }

    // Set Sign-In Type for Sign-In Forms
    function setSignInType(type) {
        const userSignInForm = document.getElementById("userSignInForm");
        const organizerSignInForm = document.getElementById("organizerSignInForm");
        const userButton = document.querySelector("#signInModal .btn-user");
        const organizerButton = document.querySelector("#signInModal .btn-organizer");

        if (type === "user") {
            userSignInForm.style.display = "block";
            organizerSignInForm.style.display = "none";
            userButton.classList.add("active");
            organizerButton.classList.remove("active");
        } else if (type === "organizer") {
            userSignInForm.style.display = "none";
            organizerSignInForm.style.display = "block";
            organizerButton.classList.add("active");
            userButton.classList.remove("active");
        }
    }

    window.setUserType = setUserType;
    window.setSignInType = setSignInType;
});