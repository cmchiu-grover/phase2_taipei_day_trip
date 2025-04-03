import { signinArea, signupMessage, signinMessage } from "./variables.js";

async function signup() {
  const username = document.getElementById("signup_name").value;
  const email = document.getElementById("signup_email").value;
  const password = document.getElementById("signup_password").value;

  try {
    const response = await fetch("/api/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: username,
        email: email,
        password: password,
      }),
    });
    const data = await response.json();
    // console.log(data);

    if (data.ok) {
      signupMessage.textContent = "註冊成功，";
    } else {
      signupMessage.textContent = data.message + "，";
    }
  } catch (e) {
    console.log("response 失敗...");
    console.log(e);
  }
}

async function signin() {
  const email = document.getElementById("signin_email").value;
  const password = document.getElementById("signin_password").value;

  const response = await fetch("/api/user/auth", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
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
    signinMessage.textContent = data.message + "，";
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
