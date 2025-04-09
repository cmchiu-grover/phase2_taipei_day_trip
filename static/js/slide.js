import { dialogEventListeners } from "./dialog.js";
import { signinArea } from "./variables.js";
// let currentPage = 0;
// let currentKeyword = "";
// let isLoading = false;
let slideIndex = 1;

class AttractionInfo {
  constructor(attractionData) {
    this.attractionData = attractionData;
    this.createBox();
  }

  createBox() {
    this.attrInfo = document.createElement("div"); // 確保正確初始化

    this.sectionDescription = document.createElement("section");
    this.sectionDescription.id = "description";
    this.sectionDescription.textContent = `${this.attractionData.description}`;

    this.attractionAddress = document.createElement("section");
    this.attractionAddress.className = "address";
    this.addressTitle = document.createElement("h3");
    this.addressTitle.textContent = `景點地址`;
    this.addressText = document.createElement("h4");
    this.addressText.id = "address";
    this.addressText.textContent = `${this.attractionData.address}`;

    this.attractionTransport = document.createElement("section");
    this.attractionTransport.className = "transport";
    this.transportTitle = document.createElement("h3");
    this.transportTitle.textContent = `交通方式：`;
    this.transportText = document.createElement("h4");
    this.transportText.id = "transport";
    this.transportText.textContent = `${this.attractionData.transport}`;

    this.attractionAddress.appendChild(this.addressTitle);
    this.attractionAddress.appendChild(this.addressText);
    this.attractionTransport.appendChild(this.transportTitle);
    this.attractionTransport.appendChild(this.transportText);

    this.attrInfo.appendChild(this.sectionDescription);
    this.attrInfo.appendChild(this.attractionAddress);
    this.attrInfo.appendChild(this.attractionTransport);
  }

  getBox() {
    return this.attrInfo;
  }
}

class AttractionImg {
  constructor(imgUrl) {
    this.imgUrl = imgUrl;
    this.createDiv();
  }

  createDiv() {
    this.slideDiv = document.createElement("div");
    this.slideDiv.className = "mySlides fade";
    this.slideDiv.style = "display: block";
    this.slideDiv.style.backgroundImage = `url("${this.imgUrl}")`;

    // this.attrImg = document.createElement("img");
    // this.attrImg.src = this.imgUrl;
    // this.slideDiv.appendChild(this.attrImg);
  }

  getDiv() {
    return this.slideDiv;
  }
}

async function getAttractionData() {
  // console.log(isLoading, currentPage);
  const url = window.location.pathname;
  const attractionId = url.match(/\/attraction\/(\d+)/);
  const id = attractionId ? attractionId[1] : null;
  const idInput = document.querySelector("#attraction_id");
  idInput.value = id;
  const attrObject = await fetch(`/api/attraction/${id}`);

  const JSON = await attrObject.json();

  const attrData = JSON.data;

  // console.log(attrData);

  const articleArea = document.querySelector("article.attraction_info");
  const slideImgDiv = document.querySelector("div.slideshow-container");

  const attractionInfo = new AttractionInfo(attrData);
  articleArea.appendChild(attractionInfo.getBox());

  const secondSection = document.getElementById("order_form");

  const inputAttrName = document.createElement("input");
  inputAttrName.id = "attr_name";
  inputAttrName.type = "text";
  inputAttrName.hidden = "true";

  inputAttrName.value = `${attrData.name}`;
  secondSection.appendChild(inputAttrName);

  const keyInput = document.getElementById("attr_name");
  // console.log(` Input的值是：${keyInput.value}`);

  const attrName = document.getElementById("attraction_name");
  const attrCategoryMrt = document.getElementById("attraction_category_mrt");

  attrName.textContent = `${attrData.name}`;
  attrCategoryMrt.textContent = `${attrData.category} at ${attrData.mrt}`;

  //   attrData.images.forEach((url) => {
  //     console.log(url);
  //   });
  const fragment = document.createDocumentFragment();

  attrData.images.forEach((url) => {
    const imgDiv = new AttractionImg(url);
    // console.log("imgDiv:", imgDiv);
    // console.log("imgDiv.getDiv():", imgDiv.getDiv());
    try {
      fragment.appendChild(imgDiv.getDiv());
    } catch (error) {
      console.error("appendChild error:", error);
    }
  });

  const arrowDivArea = document.querySelector("div.arrow_area");

  slideImgDiv.insertBefore(fragment, arrowDivArea);

  // console.log("開始做 dot area");
  // console.log(attrData.images.length);
  const dotDivArea = document.querySelector("div.dot_area");
  for (let i = 0; i < attrData.images.length; i++) {
    let dotSpan = document.createElement("span");
    dotSpan.className = `dot_${i + 1} dot`;

    dotDivArea.appendChild(dotSpan);
    // console.log("第" + i + "個完成...");
  }
}

// Next/previous controls
function plusSlides(n) {
  showSlides((slideIndex += n));
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides((slideIndex = n));
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  // console.log(slides);
  let dots = document.getElementsByClassName("dot");
  // console.log(dots);
  if (n > slides.length) {
    slideIndex = 1;
  }
  if (n < 1) {
    slideIndex = slides.length;
  }
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  // console.log(slideIndex);
  // console.log(slides);
  slides[slideIndex - 1].style.display = "block";
  dots[slideIndex - 1].className += " active";
}

const nextArrow = document.querySelector("img.next");
nextArrow.addEventListener("click", () => plusSlides(1));

const prevArrow = document.querySelector("img.prev");
prevArrow.addEventListener("click", () => plusSlides(-1));

const dotArea = document.querySelector("div.dot_area");
dotArea.addEventListener("click", function (event) {
  let clickedDot = event.target;

  if (clickedDot.classList.contains("dot")) {
    let dotNum = clickedDot.className.match(/dot_(\d+)/);

    if (dotNum) {
      showSlides((slideIndex = parseInt(dotNum[1])));
    }
  }
});

const priceP = document.querySelector("#price");
const selectTime = document.querySelectorAll('input[name="selected_time"]');

// console.log(priceP);
// console.log(selectTime);

selectTime.forEach((checked) => {
  checked.addEventListener("change", () => {
    if (checked.value === "morning") {
      priceP.textContent = "2000元";
    } else if (checked.value === "afternoon") {
      priceP.textContent = "2500元";
    }
  });
});

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

const orderForm = document.querySelector("#order_form");

orderForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const token = localStorage.getItem("access_token");
  if (token) {
    const response = await fetch("/api/user/auth", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const result = await response.json();
    const userData = result.data;

    if (userData) {
      await bookingAttraction();
      window.location.href = "/booking";
    }
  } else {
    signinArea.showModal();
  }
});

async function bookingAttraction() {
  const attractionId = document.querySelector("#attraction_id").value;
  console.log(`id is ${attractionId}...`);

  const bookingDate = document.querySelector("#booking_date").value;
  console.log(`booking date is ${bookingDate}...`);

  const bookingTime = document.querySelector(
    'input[name="selected_time"]:checked'
  ).value;
  console.log(`booking time is ${bookingTime}...`);

  let bookingPrice = 0;
  if (bookingTime === "morning") {
    bookingPrice = 2000;
  } else {
    bookingPrice = 2500;
  }

  console.log(`booking price is ${bookingPrice} NTD...`);

  const token = localStorage.getItem("access_token");

  try {
    const response = await fetch("/api/booking", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        attractionId: attractionId,
        date: bookingDate,
        time: bookingTime,
        price: bookingPrice,
      }),
    });
    const data = await response.json();
    // console.log(data);

    if (data.ok) {
      // window.location.href = "/booking";
      console.log(data);
    } else {
      window.alert("預定失敗");
    }
  } catch (e) {
    console.log("response 失敗...");
    console.log(e);
  }
}

async function main() {
  try {
    await showSignInOut();

    await getAttractionData();

    showSlides(slideIndex);
    selectTime[0].dispatchEvent(new Event("change"));
    selectTime[0].checked = "checked";
  } catch (e) {
    console.log(e);
  }
}

main();
dialogEventListeners();
