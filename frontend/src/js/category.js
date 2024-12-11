const slider = document.getElementById("category");
const prev = document.getElementById("prev");
const next = document.getElementById("next");

let currentIndex = 0;

const updateSlider = () => {
  const offset = -currentIndex * 100; // Geser slider berdasarkan index
  slider.style.transform = `translateX(${offset}%)`;
};

prev.addEventListener("click", () => {
  currentIndex = Math.max(currentIndex - 1, 0); // Pastikan index tidak kurang dari 0
  updateSlider();
});

next.addEventListener("click", () => {
  const maxIndex = slider.children.length - 3; // Pastikan index tidak melebihi jumlah elemen - 3
  currentIndex = Math.min(currentIndex + 1, maxIndex);
  updateSlider();
});
