function openSignInModal() {
    const modal = new bootstrap.Modal(document.getElementById('signInModal'));
    modal.show();

    // Select organizer sign-in by default
    setSignInType('organizer');
    document.getElementById("organizerSignInForm").style.display = "block";
    document.getElementById("userSignInForm").style.display = "none";
}
function toggleDateTimeFields() {
    const isMulti = document.getElementById('eventTypeMulti').checked;
    document.getElementById("singleDayFields").style.display = isMulti ? 'none' : 'block';
    document.getElementById("multiDayFields").style.display = isMulti ? 'block' : 'none';
}