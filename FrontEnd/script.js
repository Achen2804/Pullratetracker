fetch(
  "https://pullratetracker-git-main-andrew-chens-projects-5158726a.vercel.app/api/api",
  { method: "HEAD" },
)
  .then((response) => {
    console.log("Response Headers:", response.headers);
  })
  .catch((error) => console.error("Error:", error));

let selectedItems = JSON.parse(sessionStorage.getItem("selectedItems")) || {};

fetch("pokedata.json")
  .then((response) => response.json())
  .then((data) => {
    const container = document.getElementById("Set-List");
    for (const [setName, details] of Object.entries(data)) {
      const option = document.createElement("option");
      option.value = setName;
      option.textContent = setName;
      container.appendChild(option);
    }
    container.addEventListener("change", function () {
      getData(this.value);
    });
  });

async function getRarityGallery(set_name, rarity) {
  const API = `https://pullratetracker-git-main-andrew-chens-projects-5158726a.vercel.app/api/api?endpoint=getset&set_name=${encodeURIComponent(set_name)}&rarity=${encodeURIComponent(rarity)}`;
  console.log(API);
  console.time("MyFunction");
  response = await fetch(API, { method: "GET" });
  const data = await response.json();
  console.timeEnd("MyFunction");
  console.log("Data received from Flask app:", data);
  const images = document.createDocumentFragment();
  for (const URL of data) {
    console.log(URL);
    const img = document.createElement("img");
    img.src = URL;
    img.style.width = "100%";
    img.style.height = "auto";
    img.loading = "lazy";
    images.appendChild(img);
  }
  console.log("Type:", typeof images);
  return images;
}
function updateSelection(setName, rarity, value) {
  console.log(setName, rarity, value);

  // Ensure the set exists
  if (!selectedItems[setName]) {
    selectedItems[setName] = {};
  }

  // Update the rarity's value
  selectedItems[setName][rarity] = value;

  // Save to sessionStorage
  sessionStorage.setItem("selectedItems", JSON.stringify(selectedItems));
}
function getData(setName) {
  
  fetch("pokedata.json")
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById("data-container");
      container.innerHTML = "";

      const SetTitle = document.createElement("h2");
      SetTitle.textContent = setName;
      SetTitle.style.textAlign = "center";
      SetTitle.style.marginBottom = "20px";
      container.appendChild(SetTitle);

      if (data[setName]) {
        const Rarities = data[setName];
        for (const RarityTuple of Rarities) {
          const subRarity = RarityTuple.Subrarities;

          const raritySection = document.createElement("div");
          raritySection.style.marginBottom = "15px";

          const menuItem = document.createElement("button");
          const menuContent = document.createElement("div");
          menuContent.style.display = "flex";
          menuContent.style.alignItems = "center";
          menuContent.style.justifyContent = "space-between";
          menuContent.style.width = "100%";
          menuItem.innerHTML = ""; // clear existing content
          menuItem.appendChild(menuContent);
          menuItem.style.padding = "12px 20px";
          menuItem.style.cursor = "pointer";
          menuItem.style.backgroundColor = "#4CAF50";
          menuItem.style.color = "white";
          menuItem.style.border = "none";
          menuItem.style.borderRadius = "8px";
          menuItem.style.width = "100%";
          menuItem.style.fontSize = "16px";
          menuItem.style.transition = "background-color 0.3s";
          menuItem.setAttribute("set_name", setName);
          menuItem.setAttribute("rarity", RarityTuple.Rarity);
          // Create text info for the rarity
          const text = document.createElement("span");
          text.innerHTML = `<strong>${RarityTuple.Rarity}: </strong> 1 in ${((1 / RarityTuple.Chances) * 100).toFixed(2)} packs`;

          // Create add, quantity, and remove
          const buttonGroup = document.createElement("div");
          buttonGroup.style.display = "flex";
          buttonGroup.style.alignItems = "center";
          buttonGroup.style.gap = "5px";

          const addButtonM = document.createElement("button");
          addButtonM.textContent = "+";
          addButtonM.onclick = (e) => {
            e.stopPropagation(); // prevent menu toggle
            quantityM.value = Math.floor(parseFloat(quantityM.value)) + 1;
            updateSelection(setName, RarityTuple.Rarity, quantityM.value);
          };
          addButtonM.classList.add("adding-button")

          const quantityM = document.createElement("input");
            quantityM.type = "number";
            quantityM.min = "0";
            quantityM.value = "0";
            quantityM.style.width = "30px";
            quantityM.value = (selectedItems[setName] && selectedItems[setName][RarityTuple.Rarity]) || 0;
            quantityM.addEventListener("input", () => {
              quantityM.value = Math.floor(parseFloat(quantityM.value));
              updateSelection(setName, RarityTuple.Rarity, quantityM.value);
          });

          const removeButtonM = document.createElement("button");
          removeButtonM.textContent = "-";
          removeButtonM.onclick = (e) => {
            e.stopPropagation(); // prevent menu toggle
              quantityM.value = Math.max(Math.floor(parseFloat(quantityM.value)) - 1, 0);
            updateSelection(setName, RarityTuple.Rarity, quantityM.value);
          };
          removeButtonM.classList.add("removing-button")

          buttonGroup.appendChild(addButtonM);
          buttonGroup.appendChild(quantityM);
          buttonGroup.appendChild(removeButtonM );

          menuContent.appendChild(text);
          menuContent.appendChild(buttonGroup);

          // Add the built content to the menuItem
          

          const setData = document.createElement("div");

          const content = document.createElement("div");
          content.style.display = "none";
          content.style.paddingLeft = "20px";
          content.style.marginTop = "10px";
          content.style.backgroundColor = "#f1f1f1";
          
          for (const SubRarityTuple of subRarity) {
            const subrarityContainer = document.createElement("div");
            subrarityContainer.style.display = "flex";
            subrarityContainer.style.alignItems = "center";
            subrarityContainer.style.gap = "10px";
            subrarityContainer.style.margin = "10px 0";

            const subrarityData = document.createElement("p");
            subrarityData.style.margin = "0";
            subrarityData.innerHTML = `<Strong>${SubRarityTuple.Rarity}: </Strong> 1 in ${((1 / SubRarityTuple.Chances) * 100).toFixed(2)} packs`;

            const addButton = document.createElement("button");
            addButton.textContent = "+";
            addButton.classList.add("adding-button");
            addButton.onclick = function () {
              let currentQ = Math.floor(parseFloat(quantity.value));
              currentQ = currentQ + 1;
              quantity.value = currentQ;
              updateSelection(setName, SubRarityTuple.Rarity, quantity.value);
            };

            const quantity = document.createElement("input");
            quantity.setAttribute("type", "number");
            quantity.setAttribute("min", "0");
            quantity.setAttribute("value", "0");
            quantity.value = (selectedItems[setName] && selectedItems[setName][SubRarityTuple.Rarity]) || 0;
            quantity.id = "quantityBoxTracker";
            quantity.style.width = "20px";
            quantity.addEventListener("input", () => {
              let currentQ = Math.floor(parseFloat(quantity.value));
              quantity.value = currentQ;
              updateSelection(setName, SubRarityTuple.Rarity, quantity.value);
            });

            const removeButton = document.createElement("button");
            removeButton.textContent = "-";
            removeButton.classList.add("removing-button");
            removeButton.onclick = function () {
              let currentQ = Math.floor(parseFloat(quantity.value));
              currentQ = Math.max(currentQ - 1, 0);
              quantity.value = currentQ;
              updateSelection(setName, SubRarityTuple.Rarity, quantity.value);
            };

            subrarityContainer.appendChild(subrarityData);
            subrarityContainer.appendChild(addButton);
            subrarityContainer.appendChild(quantity);
            subrarityContainer.appendChild(removeButton);
            content.appendChild(subrarityContainer);
          }

          let isFirstClick = true;
          menuItem.addEventListener("click", async () => {
            if (isFirstClick) {
              isFirstClick = false;
              const set = menuItem.getAttribute("set_name");
              const rarity = menuItem.getAttribute("rarity");
              const rarity_gallery = await getRarityGallery(set, rarity);
              const image_gallery = document.createElement("div");
              image_gallery.style.display = "grid";
              if (window.innerWidth > 768) {
                image_gallery.style.gridTemplateColumns = "repeat(5, 1fr)";
              } else if (window.innerWidth > 480) {
                image_gallery.style.gridTemplateColumns = "repeat(2, 1fr)";
              } else {
                image_gallery.style.gridTemplateColumns = "1fr";
              }
              image_gallery.appendChild(rarity_gallery);
              content.appendChild(image_gallery);
            }
            content.style.display =
              content.style.display === "none" ? "block" : "none";
          });

          menuItem.onmouseover = () =>
            (menuItem.style.backgroundColor = "#45a049");
          menuItem.onmouseout = () =>
            (menuItem.style.backgroundColor = "#4CAF50");
          setData.appendChild(menuItem);
          setData.appendChild(content);

          container.appendChild(setData);
        }
      }
    })
    .catch((error) => console.error("Error loading JSON:", error));
}
