const keywordNav = document.querySelector("div.keyword_nav");
const leftArrow = document.querySelector("div.left_arrow");
const rightArrow = document.querySelector("div.right_arrow");

let loadState = {
  currentPage: 0,
  currentKeyword: "",
  isLoading: false,
  slideIndex: 1,
};

const bottom = document.querySelector("#bottom");

const signinArea = document.querySelector("dialog.signin_area");
const signupArea = document.querySelector("dialog.signup_area");
const closeSigninBtn = document.querySelector("button.close_signin");
const closeSignupBtn = document.querySelector("button.close_signup");
const showSignin = document.querySelector("p.p_signin");
const showSignup = document.querySelector("p.p_signup");
const hideSigninDisplaySignup = document.querySelector(
  "#hide_signin_display_signup"
);
const hideSignupDisplaySignin = document.querySelector(
  "#hide_signup_display_signin"
);

const signoutButton = document.querySelector("#sign_out");

const signinButton = document.querySelector("#signin_button");
const signupButton = document.querySelector("#signup_button");

const searchButton = document.querySelector("#search_button");

const signupMessage = document.querySelector("#signupAreaMsg");
const signinMessage = document.querySelector("#signinAreaMsg");

const signupForm = document.querySelector("#signup_form");
const signinForm = document.querySelector("#signin_form");

export {
  keywordNav,
  leftArrow,
  rightArrow,
  loadState,
  bottom,
  signinArea,
  signupArea,
  closeSigninBtn,
  closeSignupBtn,
  showSignin,
  showSignup,
  hideSigninDisplaySignup,
  hideSignupDisplaySignin,
  signoutButton,
  signinButton,
  signupButton,
  searchButton,
  signupMessage,
  signinMessage,
  signupForm,
  signinForm,
};
