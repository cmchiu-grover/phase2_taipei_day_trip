import {
  closeSigninBtn,
  closeSignupBtn,
  showSignin,
  showSignup,
  hideSigninDisplaySignup,
  hideSignupDisplaySignin,
  signoutButton,
  signinButton,
  signinArea,
  signupArea,
  signupMessage,
  signinMessage,
  signupForm,
  signinForm,
} from "./variables.js";

import { signup, signin } from "./member.js";

function dialogEventListeners() {
  closeSigninBtn.addEventListener("click", () => {
    signinArea.close();
    signinMessage.textContent = "還沒有帳戶？";
  });

  closeSignupBtn.addEventListener("click", () => {
    signupArea.close();
    signupMessage.textContent = "已經有帳戶了？";
  });

  showSignin.addEventListener("click", () => {
    signinMessage.textContent = "還沒有帳戶？";
    signinArea.showModal();
  });

  showSignup.addEventListener("click", () => {
    signupMessage.textContent = "已經有帳戶了？";
    signupArea.showModal();
  });

  signoutButton.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.reload();
  });

  hideSigninDisplaySignup.addEventListener("click", () => {
    signinArea.close();
    signinMessage.textContent = "還沒有帳戶？";
    signupMessage.textContent = "已經有帳戶了？";
    signupArea.showModal();
  });

  hideSignupDisplaySignin.addEventListener("click", () => {
    signupArea.close();
    signupMessage.textContent = "已經有帳戶了？";
    signinMessage.textContent = "還沒有帳戶？";
    signinArea.showModal();
  });

  signinForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    await signin();
  });

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    await signup();
  });
}

export { dialogEventListeners };
