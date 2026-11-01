/* Presentation only. The Python builder supplies every lattice coordinate. */
"use strict";
(() => {
  const dataElement = document.getElementById("pattern-data");
  if (!dataElement) return;
  const data = JSON.parse(dataElement.textContent);
  const paper = document.getElementById("graph-paper");
  const beads = [...paper.querySelectorAll(".bead")];
  const epochControl = document.getElementById("epoch");
  const viewControl = document.getElementById("interpretation");
  const positionControl = document.getElementById("position");
  const colors = {R: "#ce3d49", Y: "#e0bb18", B: "#252d33", "?": "#e9edeb"};
  let selected = 0;
  document.getElementById("viewer-controls").hidden = false;

  function selectPosition(value) {
    if (!Number.isInteger(value)) return;
    selected = ((value % data.length) + data.length) % data.length;
    positionControl.value = selected;
    const epoch = data.epochs[epochControl.value];
    const entry = epoch.entries[selected];
    const code = data.candidate[selected];
    const names = {R: "red", Y: "yellow", B: "black"};
    beads.forEach(bead => bead.classList.toggle("selected", Number(bead.dataset.position) === selected));
    document.getElementById("position-title").textContent = `Position ${selected}`;
    document.getElementById("position-status").textContent = `${epoch.label}: ${entry.status}. Candidate ${names[code]}.`;
    document.getElementById("position-evidence").textContent =
      `${Object.entries(entry.counts).map(([color, n]) => `${n} ${color}`).join(", ")}; ${entry.geographic_blocks.length} geographic blocks.`;
    const ids = document.getElementById("position-sources");
    ids.replaceChildren(...entry.ids.map(id => {
      const li = document.createElement("li");
      li.textContent = id;
      return li;
    }));
  }

  function recolor() {
    const epoch = data.epochs[epochControl.value];
    const provisional = viewControl.value === "candidate";
    beads.forEach(bead => {
      const i = Number(bead.dataset.position);
      const strict = epoch.strict[i];
      const code = provisional ? data.candidate[i] : strict;
      const ellipse = bead.querySelector("ellipse");
      ellipse.setAttribute("fill", colors[code]);
      ellipse.setAttribute("stroke", provisional && strict === "?" ? "#2459a2" : "#788380");
      ellipse.setAttribute("stroke-dasharray", provisional && strict === "?" ? "4 3" : "none");
      ellipse.setAttribute("stroke-width", provisional && strict === "?" ? "2" : ".6");
      bead.querySelector(".unknown").style.display = code === "?" ? "block" : "none";
      bead.querySelector(".position-label").setAttribute("fill", code === "B" ? "#fff" : "#243c3c");
      bead.querySelector(".position-label").textContent = `${i}${code === "?" ? "?" : ""}`;
      bead.querySelector("title").textContent = `Position ${i}, string k=${bead.dataset.k}, ${code === "?" ? "unknown" : code}, ${epoch.entries[i].status}, ${bead.dataset.side} display`;
      if (bead.getAttribute("role") === "button") {
        bead.setAttribute("aria-label", bead.querySelector("title").textContent);
      }
    });
    const s = epoch.statuses;
    document.getElementById("epoch-summary").textContent =
      `${epoch.label}: ${s.supported} supported / ${s.conflicting} conflicting / ${s.insufficient} insufficient; ${epoch.agreements}/${epoch.observations} recorded-label agreement. ${provisional ? "Provisional completion; dashed blue marks unresolved positions." : "Strict view; ? preserves unresolved colors."}`;
    selectPosition(selected);
  }

  epochControl.addEventListener("change", recolor);
  viewControl.addEventListener("change", recolor);
  paper.addEventListener("click", event => {
    const bead = event.target.closest(".bead");
    if (bead) selectPosition(Number(bead.dataset.position));
  });
  paper.addEventListener("keydown", event => {
    const bead = event.target.closest(".bead");
    if (bead && ["Enter", " "].includes(event.key)) {
      event.preventDefault();
      selectPosition(Number(bead.dataset.position));
    }
  });
  positionControl.addEventListener("change", () => selectPosition(Number(positionControl.value)));
  document.getElementById("previous-position").addEventListener("click", () => selectPosition(selected - 1));
  document.getElementById("next-position").addEventListener("click", () => selectPosition(selected + 1));
  document.getElementById("numbers").addEventListener("change", event => {
    document.querySelector(".paper-scroll").classList.toggle("show-numbers", event.target.checked);
  });
  document.getElementById("zoom").addEventListener("input", event => {
    paper.style.width = `${Number(event.target.value) * 100}%`;
  });
  recolor();
})();
