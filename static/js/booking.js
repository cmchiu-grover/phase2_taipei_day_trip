import { showSignInOut } from "./member.js";
import { dialogEventListeners } from "./dialog.js";

let userName = "";
let userEmail = "";
const mainPage = document.querySelector("main.booking_page");
const footerText = document.querySelector("div.booking_page_footer_text");
const bodyBookingPage = document.querySelector("body.booking_page");
const footerBookingPage = document.querySelector("footer.booking_page");
const sectionEmpty = document.querySelector("section.empty");
const formBookingForm = document.querySelector("form.booking_order_form");
const bookingAttrImg = document.querySelector("#booking_attr_img");
const bookingNameLabel = document.querySelector("#booking_name_label");
const bookingDateLabel = document.querySelector("#booking_date_label");
const bookingTimeLabel = document.querySelector("#booking_time_label");
const bookingPriceLabel = document.querySelector("#booking_price_label");
const bookingAddressLabel = document.querySelector("#booking_address_label");
const totalPriceP = document.querySelector("#total_price");
const contactNameInput = document.querySelector("#contact_name");
const contactEmailInput = document.querySelector("#contact_email");

async function checkSignin() {
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
      mainPage.style.display = "flex";
      footerText.style.display = "flex";
      userName = userData.name;
      userEmail = userData.email;
      const divHeadline = document.querySelector("div.headline");
      divHeadline.textContent = `您好，${userName}，待預訂的行程如下：`;
    }
  } else {
    window.alert("請先登入");
    window.location.href = "/";
  }
}

async function getPreOrderData() {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/api/booking", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const data = await response.json();
  // console.log(data.data);
  if (data.data) {
    bodyBookingPage.style.height = "auto";
    footerBookingPage.style.height = "104px";
    sectionEmpty.style.display = "none";
    formBookingForm.style.display = "flex";
    bookingAttrImg.style.backgroundImage = `url("${data.data.attraction.image}")`;
    bookingNameLabel.textContent = data.data.attraction.name;
    bookingDateLabel.textContent = data.data.date;
    if (data.data.time === "morning") {
      bookingTimeLabel.textContent = "早上 9 點到下午 4 點";
    } else {
      bookingTimeLabel.textContent = "下午 4 點到晚上 10 點";
    }

    bookingPriceLabel.textContent = `新台幣 ${data.data.price} 元`;
    totalPriceP.textContent = `總價：新台幣 ${data.data.price} 元`;
    bookingAddressLabel.textContent = data.data.attraction.address;

    contactNameInput.value = userName;
    contactEmailInput.value = userEmail;
  }
}

const deleteButton = document.querySelector("#delete_booking");

async function main() {
  await checkSignin();
  await showSignInOut();
  await getPreOrderData();
}

main();
dialogEventListeners();
deleteButton.addEventListener("click", async (e) => {
  e.preventDefault();
  const token = localStorage.getItem("access_token");
  const response = await fetch("/api/booking", {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const result = await response.json();
  // console.log(result);
  if (result.ok) {
    window.location.reload();
  } else {
    window.alert(result.message);
  }
});
