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
  console.log(data.data);
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

TPDirect.setupSDK(
  159803,
  "app_5OIWI3n0raHZMQfEpvaYFhzfwmyrIB2gXRSMw9IGqKm5zqqtsCayuUnRiHxb",
  "sandbox"
);

let fields = {
  number: {
    // css selector
    element: document.querySelector("#card-number"),
    placeholder: "**** **** **** ****",
  },
  expirationDate: {
    // DOM object
    element: document.querySelector("#card-expiration-date"),
    placeholder: "MM / YY",
  },
  ccv: {
    element: document.querySelector("#card-ccv"),
    placeholder: "ccv",
  },
};

TPDirect.card.setup({
  fields: fields,
  styles: {
    // Style all elements
    input: {
      color: "gray",
    },
    // Styling ccv field
    "input.ccv": {
      // 'font-size': '16px'
    },
    // Styling expiration-date field
    "input.expiration-date": {
      // 'font-size': '16px'
    },
    // Styling card-number field
    "input.card-number": {
      // 'font-size': '16px'
    },
    // style focus state
    ":focus": {
      // 'color': 'black'
    },
    // style valid state
    ".valid": {
      color: "green",
    },
    // style invalid state
    ".invalid": {
      color: "red",
    },
    // Media queries
    // Note that these apply to the iframe, not the root window.
    "@media screen and (max-width: 400px)": {
      input: {
        // color: "orange",
      },
    },
  },
  // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
  isMaskCreditCardNumber: true,
  maskCreditCardNumberRange: {
    beginIndex: 6,
    endIndex: 11,
  },
});

TPDirect.card.onUpdate(function (update) {
  // update.canGetPrime === true
  // --> you can call TPDirect.card.getPrime()
  if (update.canGetPrime) {
    // Enable submit Button to get prime.
    // submitButton.removeAttribute('disabled')
  } else {
    // Disable submit Button to get prime.
    // submitButton.setAttribute('disabled', true)
  }

  // cardTypes = ['mastercard', 'visa', 'jcb', 'amex', 'unknown']
  if (update.cardType === "visa") {
    // Handle card type visa.
  }

  // number 欄位是錯誤的
  if (update.status.number === 2) {
    // setNumberFormGroupToError()
  } else if (update.status.number === 0) {
    // setNumberFormGroupToSuccess()
  } else {
    // setNumberFormGroupToNormal()
  }

  if (update.status.expiry === 2) {
    // setNumberFormGroupToError()
  } else if (update.status.expiry === 0) {
    // setNumberFormGroupToSuccess()
  } else {
    // setNumberFormGroupToNormal()
  }

  if (update.status.ccv === 2) {
    // setNumberFormGroupToError()
  } else if (update.status.ccv === 0) {
    // setNumberFormGroupToSuccess()
  } else {
    // setNumberFormGroupToNormal()
  }
});

function onSubmit(event) {
  event.preventDefault();

  // 取得 TapPay Fields 的 status
  const tappayStatus = TPDirect.card.getTappayFieldsStatus();

  // 確認是否可以 getPrime
  if (tappayStatus.canGetPrime === false) {
    alert("can not get prime");
    return;
  }

  // Get prime
  TPDirect.card.getPrime(async (result) => {
    if (result.status !== 0) {
      console.log("get prime error " + result.msg);
      return;
    }
    console.log("get prime 成功，prime: ");
    console.log(result);

    const token = localStorage.getItem("access_token");
    const bookingResponse = await fetch("/api/booking", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const bookingData = await bookingResponse.json();
    const userPhone = document.querySelector("#contact_phone").value;
    const orderResponse = await fetch("/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        prime: result.card.prime,
        order: {
          price: bookingData.data.price,
          trip: {
            attraction: {
              id: bookingData.data.attraction.id,
              name: bookingData.data.attraction.name,
              address: bookingData.data.attraction.address,
              image: bookingData.data.attraction.image,
            },
            date: bookingData.data.date,
            time: bookingData.data.time,
          },
          contact: {
            name: userName,
            email: userEmail,
            phone: userPhone,
          },
        },
      }),
    });
    const orderResult = await orderResponse.json();
    if (!orderResult.data) {
      window.alert(`${orderResult.message}`);
      return;
    }

    if (orderResult.data.payment.status === 0) {
      const deleteResponse = await fetch("/api/booking", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      window.location.href = `/thankyou?number=${orderResult.data.number}`;
    } else {
      window.alert(`${orderResult.message}`);
      return;
    }

    // send prime to your server, to pay with Pay by Prime API .
    // Pay By Prime Docs: https://docs.tappaysdk.com/tutorial/zh/back.html#pay-by-prime-api
  });
}

// async function sendOrderData() {
//   const token = localStorage.getItem("access_token");
//   try {
//     const response = await fetch("/api/order", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         Authorization: `Bearer ${token}`,
//       },
//       body: JSON.stringify({
//         prime: prime,
//         order: {
//           price: price,
//           trip: {
//             attraction: {
//               id: attrationId,
//               name: attrationName,
//               address: attrationAdress,
//               image: imgUrl,
//             },
//             date: bookingDate,
//             time: bookingTime,
//           },
//           contact: {
//             name: userName,
//             email: userEmail,
//             phone: userPhone,
//           },
//         },
//       }),
//     });

//     const data = await response.json();
//     if (data.ok) {
//       console.log(data);
//     } else {
//       window.alert("訂單失敗");
//     }
//   } catch (e) {
//     console.log("response 失敗...");
//     console.log(e);
//   }
// }

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
formBookingForm.addEventListener("submit", onSubmit);
