const usernameField = document.querySelector("#usernameField");
const userfeedBackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".invalid_email_feedback");
const usernamesuccessOutput = document.querySelector(".usernamesuccessOutput");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const passwordField = document.querySelector("#passwordField");
const submitBtn = document.querySelector('.submit-btn');
const handleToggleInput=(e)=>{
  if(showPasswordToggle.textContent === "SHOW"){
    showPasswordToggle.textContent = "HIDE";
    passwordField.setAttribute("type","text");
  }
  else{
    showPasswordToggle.textContent = "SHOW";
    passwordField.setAttribute("type","password");
  }
}

showPasswordToggle.addEventListener("click",handleToggleInput);




usernameField.addEventListener("keyup", (e) => {
  const usernameVal = e.target.value;

  console.log("usernameVal", usernameVal);
  if (usernameVal.length > 0) {
    usernamesuccessOutput.style.display = "block";
    usernamesuccessOutput.textContent = `Checking ${usernameVal}`;
    usernameField.classList.remove("is-invalid");
    userfeedBackArea.style.display = "none";
    fetch("/authentication/validate-username/", {
      body: JSON.stringify({ username: usernameVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        usernamesuccessOutput.style.display = "none";
        if (data.username_error) {
          submitBtn.disabled = true;
          usernameField.classList.add("is-invalid");
          userfeedBackArea.style.display = "block";
          userfeedBackArea.innerHTML = `<p>${data.username_error}</p>`;
        }
        else{
          submitBtn.removeAttribute('disabled');
        }
      });
  }
});
emailField.addEventListener("keyup", (e) => {
  const emailVal = e.target.value;
  console.log("emailVal", emailVal);
  if (emailVal.length > 0) {
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = "none";
    fetch("/authentication/validate-email/", {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        if (data.email_error) {
          submitBtn.disabled = true;
          emailField.classList.add("is-invalid");
          emailFeedBackArea.style.display = "block";
          emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
        }
        else{
          submitBtn.removeAttribute('disabled');
        }
        
        
      });
  }
});
