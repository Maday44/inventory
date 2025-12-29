const container = document.getElementById('error-403');
const jail = document.getElementById('jail');

let seenMouse = false;

document.addEventListener('mousemove', mouseUpdate);
document.addEventListener('mouseenter', mouseUpdate);
document.addEventListener('mouseleave', mouseLeft);

function mouseUpdate(e) {
  const jailCoords = jail.getBoundingClientRect();
  const pageCoords = container.getBoundingClientRect();

  const x = e.pageX - jailCoords.left;
  const y = e.pageY - jailCoords.top;

  container.style.setProperty('--mouseX', x);
  container.style.setProperty('--mouseY', y);
  container.style.setProperty('--width', pageCoords.width);
  container.style.setProperty('--height', pageCoords.height);

  if (!seenMouse) {
    container.classList.add('seenMouse');
    seenMouse = true;
  }
}

function mouseLeft() {
  container.classList.remove('seenMouse');
  seenMouse = false;
}
