document.querySelectorAll("[data-repeat]").forEach((block) => {
  const addButton = block.querySelector("[data-add-repeat]");
  const list = block.querySelector("[data-repeat-list]");
  const max = Number(block.dataset.max || 10);

  addButton?.addEventListener("click", () => {
    const current = list.querySelectorAll("input").length;
    if (current >= max) return;
    const firstInput = list.querySelector("input");
    const label = document.createElement("label");
    label.textContent = "Instagram post link";
    const input = document.createElement("input");
    input.name = firstInput?.name || "instagram_links";
    input.placeholder = "https://www.instagram.com/p/...";
    label.appendChild(input);
    list.appendChild(label);
  });
});

document.querySelectorAll("[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    const message = form.dataset.confirm || "Are you sure?";
    if (!window.confirm(message)) {
      event.preventDefault();
    }
  });
});
