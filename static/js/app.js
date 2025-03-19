async function getMrts() {
  let mrtObject = await fetch("/api/mrts");
  let JSON = await mrtObject.json();
  let mrtList = JSON.data;
  const keywordArea = document.querySelector("div.keyword_nav");
  for (let i = 0; i < mrtList.length; i++) {
    let keywordDiv = document.createElement("div");
    keywordDiv.textContent = `${mrtList[i]}`;
    keywordDiv.setAttribute(
      "onclick",
      "quicklySearch(event, this.textContent)"
    );

    keywordArea.appendChild(keywordDiv);
    // console.log(mrtList[i]);
  }
}

getMrts();

const keywordNav = document.querySelector("div.keyword_nav");
const leftArrow = document.querySelector("div.left_arrow");
const rightArrow = document.querySelector("div.right_arrow");

leftArrow.addEventListener("click", () => {
  keywordNav.scrollLeft -= 500; // 向左滾動 100px
});

rightArrow.addEventListener("click", () => {
  keywordNav.scrollLeft += 500; // 向右滾動 100px
});

async function getAttractions(pageNumber = 0, keyword = "") {
  const attrObject = await fetch(
    `/api/attractions?page=${pageNumber}&keyword=${keyword}`
  );
  const JSON = await attrObject.json();
  const attrList = JSON.data;
  const articleArea = document.querySelector("article");
  const boxArea = document.createElement("div");
  boxArea.className = "box_area";
  if (!JSON.nextPage) {
    window.removeEventListener("scroll", addMoreAttractionsHandler);
  }

  for (let i = 0; i < attrList.length; i++) {
    let attractionName = attrList[i].name;
    let mrtName = attrList[i].mrt;
    let categoryName = attrList[i].category;
    let attrBox = document.createElement("div");
    attrBox.className = "box";
    let imgContainer = document.createElement("figure");
    imgContainer.style.backgroundImage = `url(${attrList[i].images[0]})`;
    let p_tag = document.createElement("p");
    p_tag.textContent = `${attractionName}`;
    imgContainer.appendChild(p_tag);
    boxArea.appendChild(imgContainer);
    let attractionText = document.createElement("div");
    attractionText.className = "attraction_text";
    let mrtStation = document.createElement("div");
    mrtStation.className = "mrt_station";
    let categoryDiv = document.createElement("div");
    categoryDiv.className = "category";
    mrtStation.textContent = `${mrtName}`;
    categoryDiv.textContent = `${categoryName}`;
    attractionText.appendChild(mrtStation);
    attractionText.appendChild(categoryDiv);
    attrBox.appendChild(imgContainer);
    attrBox.appendChild(attractionText);
    boxArea.appendChild(attrBox);
  }
  articleArea.appendChild(boxArea);
  return JSON.nextPage;
}

async function loadAttractions() {
  currentPage = await getAttractions();
  if (currentPage == null) {
    return;
  }

  while (window.innerHeight > document.body.offsetHeight) {
    currentPage = await getAttractions(currentPage);
    if (currentPage == null) {
      break;
    }
  }
}

async function addMoreAttractions() {
  const threshold = document.documentElement.scrollHeight * 0.9;
  if (window.innerHeight + window.scrollY >= threshold) {
    window.removeEventListener("scroll", addMoreAttractionsHandler);
    const nextPage = await getAttractions(currentPage, currentKeyword);
    if (nextPage !== null) {
      currentPage = nextPage;
      window.addEventListener("scroll", addMoreAttractionsHandler);
    }
  }
}

async function searchAttraction(event) {
  event.preventDefault();

  const keywordInput = document.getElementById("keyword");

  if (keywordInput.value.trim() === "") {
    alert("請先輸入內容再送出...");
    return;
  }

  const articleArea = document.querySelector("article");

  console.log(`先刪除內容`);

  while (articleArea.firstChild) {
    articleArea.removeChild(articleArea.firstChild);
  }

  console.log(`開始搜尋`);
  currentKeyword = keywordInput.value.trim();
  currentPage = 0;
  const nextPage = await getAttractions(currentPage, currentKeyword);

  if (nextPage !== null) {
    currentPage = nextPage;
    window.addEventListener("scroll", addMoreAttractionsHandler);
  }
}

async function quicklySearch(event, keyword) {
  event.preventDefault();
  const keywordInput = document.getElementById("keyword");
  keywordInput.value = keyword;
  const articleArea = document.querySelector("article");

  console.log(`先刪除內容`);

  while (articleArea.firstChild) {
    articleArea.removeChild(articleArea.firstChild);
  }

  console.log(`開始搜尋`);
  const nextPage = await getAttractions(0, keyword.trim());

  if (nextPage !== null) {
    currentPage = nextPage;
    window.addEventListener("scroll", addMoreAttractions(keyword.trim()));
  }
}

function throttle(func, delay) {
  let timerId;
  return function (...args) {
    if (!timerId) {
      timerId = setTimeout(() => {
        func.apply(this, args);
        timerId = undefined;
      }, delay);
    }
  };
}

let currentPage = 0;
let currentKeyword = "";

const addMoreAttractionsHandler = throttle(() => addMoreAttractions(), 300);
loadAttractions().then(() => {
  window.addEventListener("scroll", addMoreAttractionsHandler);
});

function displaySignin() {
  const signinArea = document.querySelector("div.signin_area");
  const coverPaper = document.querySelector("div.cover");
  signinArea.style.display = "flex";
  coverPaper.style.display = "flex";
}

function displaySignup() {
  const signupArea = document.querySelector("div.signup_area");
  const coverPaper = document.querySelector("div.cover");
  signupArea.style.display = "flex";
  coverPaper.style.display = "flex";
}

function hideSignin() {
  const signinArea = document.querySelector("div.signin_area");
  const coverPaper = document.querySelector("div.cover");
  signinArea.style.display = "none";
  coverPaper.style.display = "none";
}

function hideSignup() {
  const signupArea = document.querySelector("div.signup_area");
  const coverPaper = document.querySelector("div.cover");
  signupArea.style.display = "none";
  coverPaper.style.display = "none";
}

function hideSigninDisplaySignup() {
  const signinArea = document.querySelector("div.signin_area");
  const signupArea = document.querySelector("div.signup_area");
  signinArea.style.display = "none";
  signupArea.style.display = "flex";
}

function hideSignupDisplaySignin() {
  const signinArea = document.querySelector("div.signin_area");
  const signupArea = document.querySelector("div.signup_area");
  signinArea.style.display = "flex";
  signupArea.style.display = "none";
}
