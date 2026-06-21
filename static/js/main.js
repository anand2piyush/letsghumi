const rotateImageSliders = () => {
  document.querySelectorAll(".trip-image-slider").forEach((slider) => {
    const images = [...slider.querySelectorAll("img")];
    if (images.length <= 1) return;
    let index = images.findIndex((image) => image.classList.contains("active"));
    if (index < 0) index = 0;
    images[index].classList.remove("active");
    images[(index + 1) % images.length].classList.add("active");
  });
};

const scrollInstagramStrips = () => {
  document.querySelectorAll("[data-auto-scroll]").forEach((strip) => {
    const firstCard = strip.firstElementChild;
    if (!firstCard) return;
    if (strip.scrollWidth <= strip.clientWidth) return;
    const step = firstCard.getBoundingClientRect().width + 12;
    const nearEnd = strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 8;
    strip.scrollTo({ left: nearEnd ? 0 : strip.scrollLeft + step, behavior: "smooth" });
  });
};

const processInstagramEmbeds = () => {
  if (window.instgrm?.Embeds?.process) {
    window.instgrm.Embeds.process();
  }
};

window.setInterval(rotateImageSliders, 5000);
window.setInterval(scrollInstagramStrips, 5000);
window.addEventListener("load", processInstagramEmbeds);
