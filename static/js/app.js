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

let currentPage = 0;
let currentKeyword = "";
let isLoading = false;

async function getAttractions() {
  // console.log(isLoading, currentPage);
  if (isLoading || currentPage === null) return;
  isLoading = true;

  const attrObject = await fetch(
    `/api/attractions?page=${currentPage}&keyword=${currentKeyword}`
  );
  const JSON = await attrObject.json();
  const attrList = JSON.data;
  const articleArea = document.querySelector("article");
  const boxArea = document.createElement("div");
  boxArea.className = "box_area";

  for (let i = 0; i < attrList.length; i++) {
    let attractionName = attrList[i].name;
    let mrtName = attrList[i].mrt;
    let categoryName = attrList[i].category;
    let attrBox = document.createElement("div");
    attrBox.className = "box";
    let imgContainer = document.createElement("figure");
    imgContainer.style.backgroundImage = `url(${attrList[i].images[0]})`;
    let figcaption = document.createElement("figcaption");
    figcaption.textContent = `${attractionName}`;
    imgContainer.appendChild(figcaption);
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
    attrBox.addEventListener("click", function () {
      location.href = `attraction/${attrList[i].id}`;
    });
    boxArea.appendChild(attrBox);
  }

  articleArea.appendChild(boxArea);

  currentPage = JSON.nextPage;
  isLoading = false;

  if (!currentPage) {
    // console.log(`監控關閉...`);
    observer.unobserve(bottom);
    // console.log("沒有更多資料...");
  }
}

const bottom = document.querySelector("#bottom");

const observer = new IntersectionObserver(async (entries) => {
  if (entries[0].isIntersecting && !isLoading) {
    // console.log(`發動監控，目前頁碼為：${currentPage}`);
    loadAttractions();
  }
});

async function loadAttractions() {
  await getAttractions();
  if (document.documentElement.scrollHeight <= window.innerHeight) {
    // console.log("視窗太大，載入更多資料...");
    await getAttractions();
  }
}

loadAttractions();
observer.observe(bottom);

async function searchAttraction(event) {
  event.preventDefault();
  const keywordInput = document.getElementById("keyword");
  if (keywordInput.value.trim() === "") {
    alert("請先輸入內容再送出...");
    return;
  }
  const articleArea = document.querySelector("article");
  // console.log(`先刪除內容`);

  while (articleArea.firstChild) {
    articleArea.removeChild(articleArea.firstChild);
  }

  // console.log(`開始搜尋`);
  currentKeyword = keywordInput.value.trim();
  currentPage = 0;
  // console.log(`第 ${currentPage} 頁資料`);
  observer.observe(bottom);
  loadAttractions();
}

async function quicklySearch(event, keyword) {
  event.preventDefault();
  const keywordInput = document.getElementById("keyword");
  keywordInput.value = keyword;
  const articleArea = document.querySelector("article");

  // console.log(`先刪除內容`);

  while (articleArea.firstChild) {
    articleArea.removeChild(articleArea.firstChild);
  }

  // console.log(`開始搜尋`);
  currentKeyword = keywordInput.value.trim();
  currentPage = 0;
  // console.log(`第 ${currentPage} 頁資料`);
  observer.observe(bottom);
  loadAttractions();
}

const signinArea = document.querySelector("dialog.signin_area");
const signupArea = document.querySelector("dialog.signup_area");
const closeSigninBtn = document.querySelector("img.close_signin");
const closeSignupBtn = document.querySelector("img.close_signup");
const showSignin = document.querySelector("p.p_signin");
const showSignup = document.querySelector("p.p_signup");

showSignin.addEventListener("click", () => {
  signinArea.showModal();
});

showSignup.addEventListener("click", () => {
  signupArea.showModal();
});

function closeSignin() {
  signinArea.close();
}

function closeSignup() {
  signupArea.close();
}

function closeSigninShowSignup() {
  signinArea.close();
  signupArea.showModal();
}

function closeSignupShowSignin() {
  signupArea.close();
  signinArea.showModal();
}
