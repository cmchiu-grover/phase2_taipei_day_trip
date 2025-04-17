import { showSignInOut } from "./member.js";
import { dialogEventListeners } from "./dialog.js";

const url = new URLSearchParams(window.location.search);
const orderNumber = url.get("number");
document.getElementById("thanks").textContent = orderNumber;

async function main() {
  await showSignInOut();
}

main();
dialogEventListeners();
