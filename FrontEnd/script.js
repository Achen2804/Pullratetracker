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
    const fragment = [];
    for (const [setName, details] of Object.entries(data)) {
      const option = document.createElement("option");
      option.value = setName;
      option.textContent = setName;
      fragment.push(option);
    }
    fragment.sort((a, b) => a.textContent.localeCompare(b.textContent));
    container.appendChild(...fragment);
    container.addEventListener("change", function () {
      getData(this.value);
    });
  });


  function saveToSessionCache(setName, rarity, imageUrls) {
    const cacheKey = `${setName}-${rarity}`;
    const cache = JSON.parse(sessionStorage.getItem("imageCache") || "{}");
    cache[cacheKey] = imageUrls;
    sessionStorage.setItem("imageCache", JSON.stringify(cache));
  }
  
  function loadFromSessionCache(setName, rarity) {
    const cache = JSON.parse(sessionStorage.getItem("imageCache") || "{}");
    return cache[`${setName}-${rarity}`] || null;
  }
async function getRarityGallery(set_name, rarity) {
  
  console.time("MyFunction");
  const cacheKey = `imageCache-${set_name}-${rarity}`;
  let data;
  data = loadFromSessionCache(set_name, rarity);
  if (data == null) {
    const API = `https://pullratetracker-git-main-andrew-chens-projects-5158726a.vercel.app/api/api?endpoint=getset&set_name=${encodeURIComponent(set_name)}&rarity=${encodeURIComponent(rarity)}`;
    console.log(API);
    response = await fetch(API, { method: "GET" });
    data = await response.json();
    saveToSessionCache(set_name, rarity, data);
    console.log("Data received from Flask app:", data);
    console.log(data)
    console.timeEnd("MyFunction");
  }
  
  
  
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
function updateSelection(setName, rarity, value,specificOdds) {
  console.log(setName, rarity, value);

  // Ensure the set exists
  if (!selectedItems[setName]) {
    selectedItems[setName] = {};
  }
  if(!selectedItems[setName][rarity]){
    selectedItems[setName][rarity] = {'Quantity':0,'Probability':0};
  }
  // Update the rarity's value
  selectedItems[setName][rarity]['Quantity'] = value;
  selectedItems[setName][rarity]['Probability'] = specificOdds;

  // Save to sessionStorage
  sessionStorage.setItem("selectedItems", JSON.stringify(selectedItems));
}
function getData(setName) {
  sessionStorage.setItem("currentSetName", setName);
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
          const specificOddsRarity = RarityTuple.SpecificRarity;
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
          menuItem.setAttribute("rarity", RarityTuple.Rarity);          // Create text info for the rarity
          const text = document.createElement("span");
          text.innerHTML = `<strong>${RarityTuple.Rarity}: </strong> 1 in ${((1 / RarityTuple.Chances) * 100).toFixed(2)} packs`;

          // Create add, quantity, and remove
          
          const genericOddsRarity = RarityTuple.Chances / 100;
          const count = Math.round(genericOddsRarity/specificOddsRarity);
          console.log(RarityTuple.Rarity, count);
          const buttonGroup = document.createElement("div");
          buttonGroup.style.display = "flex";
          buttonGroup.style.alignItems = "center";
          buttonGroup.style.gap = "5px";

          const addButtonM = document.createElement("button");
          addButtonM.classList.add("adding-button")
          addButtonM.textContent = "+";
          addButtonM.onclick = (e) => {
            e.stopPropagation(); // prevent menu toggle
            quantityM.value = Math.min(Math.floor(parseFloat(quantityM.value)) + 1,count);
            updateSelection(setName, RarityTuple.Rarity, quantityM.value, specificOddsRarity);
          };
          
          const quantityM = document.createElement("input");
            quantityM.type = "number";
            quantityM.min = "0";
            quantityM.value = "0";
            quantityM.max = count.toString();
            quantityM.style.width = "30px";
            quantityM.value = selectedItems[setName]?.[RarityTuple.Rarity]?.Quantity || 0;
            quantityM.addEventListener("input", () => {
              quantityM.value = Math.floor(parseFloat(quantityM.value));
              updateSelection(setName, RarityTuple.Rarity, quantityM.value,specificOddsRarity);
          });

          const removeButtonM = document.createElement("button");
          removeButtonM.textContent = "-";
          removeButtonM.onclick = (e) => {
            e.stopPropagation(); // prevent menu toggle
              quantityM.value = Math.max(Math.floor(parseFloat(quantityM.value)) - 1, 0);
            updateSelection(setName, RarityTuple.Rarity, quantityM.value, specificOddsRarity);
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
            const specificOdds = SubRarityTuple.SpecificRarity
            const genericOdds = SubRarityTuple.Chances / 100
            const count = Math.round(genericOdds/specificOdds)
            const addButton = document.createElement("button");
            addButton.textContent = "+";
            addButton.classList.add("adding-button");
            addButton.onclick = function () {
              let currentQ = Math.floor(parseFloat(quantity.value));
              currentQ = Math.min(currentQ + 1, count);
              quantity.value = currentQ;
              updateSelection(setName, SubRarityTuple.Rarity, quantity.value,specificOdds);
            };
            
            const quantity = document.createElement("input");
            quantity.setAttribute("type", "number");
            quantity.setAttribute("min", "0");
            quantity.setAttribute("max", count.toString());
            quantity.setAttribute("value", "0");
            quantity.value = (selectedItems[setName] && selectedItems[setName][SubRarityTuple.Rarity]) || 0;
            quantity.id = "quantityBoxTracker";
            quantity.style.width = "20px";
            quantity.addEventListener("input", () => {
              let currentQ = Math.floor(parseFloat(quantity.value));
              quantity.value = currentQ;
              updateSelection(setName, SubRarityTuple.Rarity, quantity.value,specificOdds);
            });

            const removeButton = document.createElement("button");
            removeButton.textContent = "-";
            removeButton.classList.add("removing-button");
            removeButton.onclick = function () {
              let currentQ = Math.floor(parseFloat(quantity.value));
              currentQ = Math.max(currentQ - 1, 0);
              quantity.value = currentQ;
              updateSelection(setName, SubRarityTuple.Rarity, quantity.value,specificOdds);
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

function calculateOdds(){
  const currentSetName = sessionStorage.getItem("currentSetName");
  const selectedItems = JSON.parse(sessionStorage.getItem("selectedItems")) || {}; 
  const relevantItems = selectedItems[currentSetName]
  console.log(relevantItems)
  let p = 0;
  for (const [rarity, data] of Object.entries(relevantItems)){
    const Quantity = data.Probability
    const Odds = data.Quantity
    p += Quantity*Odds
  }
  console.log(p)
  console.log('Begin')
  const odds = (1/(p)).toFixed(2);
  console.log(odds)
  console.log("End")
  return odds;
}
function displayChances(){
  const box = document.getElementById("probability-box")
  box.textContent = calculateOdds();
}
