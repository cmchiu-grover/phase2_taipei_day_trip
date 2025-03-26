let currentPage = 0;
let currentKeyword = "";
let isLoading = false;
let mutux = Promise.then;

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

  // 提取 id
  const id = attractionId ? attractionId[1] : null;

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
  for (i = 0; i < attrData.images.length; i++) {
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
  slides[slideIndex - 1].style.display = "block";
  dots[slideIndex - 1].className += " active";
}

async function main() {
  try {
    await getAttractionData();

    // console.log(`完成 getAttractionData()`);

    showSlides(slideIndex);
  } catch (e) {
    console.log(e);
  }
}

let slideIndex = 1;
main();

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

console.log(priceP);
console.log(selectTime);

selectTime.forEach((checked) => {
  checked.addEventListener("change", () => {
    if (checked.value === "gozen") {
      priceP.textContent = "2000元";
    } else if (checked.value === "gogo") {
      priceP.textContent = "2500元";
    }
  });
});
