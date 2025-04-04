import {
  keywordNav,
  leftArrow,
  rightArrow,
  loadState,
  // currentPage,
  // currentKeyword,
  // isLoading,
  bottom,
  signinArea,
  signupArea,
  searchButton,
} from "./variables.js";

import { showSignInOut } from "./member.js";

import { dialogEventListeners } from "./dialog.js";

async function getMrts() {
  let mrtObject = await fetch("/api/mrts");
  let JSON = await mrtObject.json();
  let mrtList = JSON.data;
  const keywordArea = document.querySelector("div.keyword_nav");

  for (let i = 0; i < mrtList.length; i++) {
    let keywordDiv = document.createElement("div");
    keywordDiv.textContent = `${mrtList[i]}`;
    keywordDiv.addEventListener("click", function (event) {
      quicklySearch(event, this.textContent);
    });

    keywordArea.appendChild(keywordDiv);
  }
}

leftArrow.addEventListener("click", () => {
  keywordNav.scrollLeft -= 500; // 向左滾動 100px
});

rightArrow.addEventListener("click", () => {
  keywordNav.scrollLeft += 500; // 向右滾動 100px
});

async function getAttractions() {
  // console.log(isLoading, currentPage);
  if (loadState.isLoading || loadState.currentPage === null) return;
  loadState.isLoading = true;

  const attrObject = await fetch(
    `/api/attractions?page=${loadState.currentPage}&keyword=${loadState.currentKeyword}`
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

  loadState.currentPage = JSON.nextPage;
  loadState.isLoading = false;

  if (!loadState.currentPage) {
    // console.log(`監控關閉...`);
    observer.unobserve(bottom);
    // console.log("沒有更多資料...");
  }
}

const observer = new IntersectionObserver(async (entries) => {
  if (entries[0].isIntersecting && !loadState.isLoading) {
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
  loadState.currentKeyword = keywordInput.value.trim();
  loadState.currentPage = 0;
  // console.log(`第 ${currentPage} 頁資料`);
  observer.observe(bottom);
  loadAttractions();
}

searchButton.addEventListener("click", async (event) => {
  searchAttraction(event);
});

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
  loadState.currentKeyword = keywordInput.value.trim();
  loadState.currentPage = 0;
  // console.log(`第 ${currentPage} 頁資料`);
  observer.observe(bottom);
  loadAttractions();
}

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

async function main() {
  showSignInOut();

  getMrts();

  loadAttractions();
  observer.observe(bottom);
}

main();
dialogEventListeners();
