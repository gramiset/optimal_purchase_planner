function passwordCheck() {
    var pwd = document.getElementById("pwd");
    var cpwd = document.getElementById("cpwd");
    cpwd.setCustomValidity("");
    if (pwd.value != cpwd.value) {
       cpwd.setCustomValidity("Passwords do not match.");
    }
}

function changePasswordCheck() {
    var opwd = document.getElementById("opwd");
    var pwd = document.getElementById("pwd");
    var cpwd = document.getElementById("cpwd");
    cpwd.setCustomValidity('');
    if (opwd.value == pwd.value) {
       cpwd.setCustomValidity("Old and New Password should not be same.");
    } else if (pwd.value != cpwd.value) {
       cpwd.setCustomValidity("New and Confirm Passwords do not match.");
    }
}


function captchaCheck() {
    var response = grecaptcha.getResponse();
    if(response.length == 0) {
        document.getElementById("error").innerHTML = "Please select the CAPTCHA checkbox.";
        return false;
    } else {
        document.getElementById("error").innerHTML = "";
        return true;
    }
}

function populateGender(gender) {
    var gender_radio = document.getElementById('gender')
    innerHTML = '<input class="first-input" type="radio" name="gender" value="Male"'
    innerHTML += (gender === 'Male' || gender === 'M') ? ' checked' : ''
    innerHTML += ' required>Male'
    innerHTML += '<input type="radio" name="gender" value="Female"'
    innerHTML += (gender === 'Female' || gender === 'F') ? ' checked' : ''
    innerHTML += '>Female'
    innerHTML += '<input type="radio" name="gender" value="Other"'
    innerHTML += (gender === 'Other' || gender === 'O') ? ' checked' : ''
    innerHTML += '>Other'
    gender_radio.innerHTML = innerHTML
}

