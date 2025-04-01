import {
  signupArea,
  signinArea,
  signupMessage,
  hideSignupDisplaySignin,
  hideSigninDisplaySignup,
  signinMessage,
} from "./variables.js";

async function signup() {
  const username = document.getElementById("signup_name").value;
  const email = document.getElementById("signup_email").value;
  const password = document.getElementById("signup_password").value;

  if (email.trim() === "" || password.trim() === "" || email.trim() === "") {
    alert("請先輸入資料再送出...");
    return;
  }

  try {
    const response = await fetch("/api/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `name=${username}&email=${email}&password=${password}`,
    });
    const data = await response.json();
    // console.log(data);

    if (data.ok) {
      if (hideSignupDisplaySignin.textContent.trim() === "") {
        hideSignupDisplaySignin.textContent = "點此登入";
      }
      signupMessage.textContent = "註冊成功，";
    } else {
      hideSignupDisplaySignin.textContent = "";
      signupMessage.textContent = data.message;
    }
  } catch (e) {
    console.log("response 失敗...");
    console.log(e);
  }
}

async function signin(event) {
  event.preventDefault();
  const email = document.getElementById("signin_email").value;
  const password = document.getElementById("signin_password").value;

  if (email.trim() === "" || password.trim() === "") {
    alert("請先輸入帳號或密碼再送出...");
    return;
  }

  const response = await fetch("/api/user/auth", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `email=${email}&password=${password}`,
  });

  const data = await response.json();
  if (data.token) {
    // console.log(data);
    const token = data.token;
    // console.log(token);

    localStorage.setItem("access_token", token);

    signinArea.close();
    window.location.reload();
  } else {
    hideSigninDisplaySignup.textContent = "";
    signinMessage.textContent = data.message;
  }
}

async function showSignInOut() {
  const token = localStorage.getItem("access_token");
  const signInUP = document.querySelector("#sign_in_up");
  const signOut = document.querySelector("#sign_out");

  if (token) {
    const response = await fetch("/api/user/auth", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const JSON = await response.json();
    const userData = JSON.data;

    if (userData) {
      signInUP.style.display = "none";
      signOut.style.display = "flex";
    }
  } else {
    signOut.style.display = "none";
    signInUP.style.display = "flex";
  }
}

export { signup, signin, showSignInOut };
