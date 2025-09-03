// ------- multi-step form wiring -------
const form = document.querySelector("form#event-form") || document.querySelector("form");
const formSteps = document.querySelectorAll(".form-step");
const btnNext = document.querySelectorAll("[data-next]");
const btnPrev = document.querySelectorAll("[data-prev]");
let formStepIndex = 0;

function showStep(i) {
  formSteps.forEach((s, idx) => {
    s.style.display = idx === i ? "block" : "none";
    // lift required only on the visible step
    Array.from(s.querySelectorAll("[required]")).forEach(el => {
      if (idx === i) el.removeAttribute("data-temp-removed");
      if (idx !== i && el.hasAttribute("required")) {
        el.setAttribute("data-temp-removed", "1");
        el.removeAttribute("required");
      }
    });
  });
  // re-apply required on the visible step
  Array.from(formSteps[i].querySelectorAll("[data-temp-removed='1']")).forEach(el => {
    el.setAttribute("required", "required");
    el.removeAttribute("data-temp-removed");
  });
}

function validateStep(i) {
  const step = formSteps[i];
  if (!step) return true;
  const required = step.querySelectorAll("[required]");
  for (const el of required) {
    if (!el.value || (el.type === "checkbox" && !el.checked)) {
      el.focus();
      return false;
    }
  }
  return true;
}

btnNext.forEach(b => b.addEventListener("click", e => {
  e.preventDefault();
  if (!validateStep(formStepIndex)) return;
  if (formStepIndex < formSteps.length - 1) {
    formStepIndex++;
    showStep(formStepIndex);
    if (formStepIndex === formSteps.length - 1) buildSummary();
  }
}));

btnPrev.forEach(b => b.addEventListener("click", e => {
  e.preventDefault();
  if (formStepIndex > 0) {
    formStepIndex--;
    showStep(formStepIndex);
  }
}));

// Enter key → next step (except last step, where it submits)
form.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  const tag = (e.target.tagName || "").toLowerCase();
  const type = (e.target.type || "").toLowerCase();
  if (tag === "textarea" || type === "file") return;

  if (formStepIndex < formSteps.length - 1) {
    e.preventDefault();
    if (!validateStep(formStepIndex)) return;
    formStepIndex++;
    showStep(formStepIndex);
    if (formStepIndex === formSteps.length - 1) buildSummary();
  } else {
    // final step: allow submit only if valid
    if (!validateStep(formStepIndex)) e.preventDefault();
  }
});

function buildSummary() {
  // Optional: show a summary preview (depends on your HTML)
  const out = document.getElementById("summary-list");
  if (!out) return;
  const fields = [
    ["Event Name", document.getElementById("event_name")?.value],
    ["Venue", document.getElementById("venue")?.value],
    ["Start", `${document.getElementById("start_date")?.value} ${document.getElementById("start_time")?.value}`.trim()],
    ["End", `${document.getElementById("end_date")?.value} ${document.getElementById("end_time")?.value}`.trim()],
    ["Attendance", document.getElementById("attendance")?.value],
  ];
  out.innerHTML = fields.map(([k, v]) => `<li><strong>${k}:</strong> ${v || "-"}</li>`).join("");
}

// init
showStep(0);

// ------- ARC GIS map picker -------
(function initArcGISPicker() {
  if (!window.require || !document.getElementById("map")) return;

  require([
    "esri/Map",
    "esri/views/MapView",
    "esri/widgets/Search",
    "esri/Graphic",
    "esri/layers/FeatureLayer",
    "esri/rest/locator",
  ], function (Map, MapView, Search, Graphic, FeatureLayer, locator) {

    const venueInput   = document.getElementById("venue");
    const latInput     = document.getElementById("latitude");
    const lonInput     = document.getElementById("longitude");
    const fidInput     = document.getElementById("arcgis_feature_id");
    const fnameInput   = document.getElementById("arcgis_feature_name");
    const layerInput   = document.getElementById("arcgis_layer");

    const map = new Map({ basemap: "streets-navigation-vector" });

    const view = new MapView({
      container: "map",
      map,
      center: [153.06, -26.65], // Sunshine Coast approx
      zoom: 10
    });

    // Search widget
    const search = new Search({ view });
    view.ui.add(search, "top-right");

    // Marker symbol
    const markerSym = {
      type: "simple-marker",
      style: "circle",
      size: 10,
      color: [0, 122, 255, 0.95],
      outline: { color: [255, 255, 255], width: 2 }
    };

    // World geocoder
    const WORLD_GEOCODER =
      "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer";

    // TODO: Replace with SCC civic land / parks FeatureLayer URL
    const civicLayer = new FeatureLayer({
      url: "YOUR_FEATURE_LAYER_URL", // e.g. https://services.arcgis.com/.../FeatureServer/0
      outFields: ["*"],
      title: "Council Land"
    });
    map.add(civicLayer);

    let pointGraphic;

    function setPoint(longitude, latitude) {
      // marker
      if (pointGraphic) view.graphics.remove(pointGraphic);
      pointGraphic = new Graphic({
        geometry: { type: "point", longitude, latitude },
        symbol: markerSym
      });
      view.graphics.add(pointGraphic);

      // hidden fields
      lonInput.value = longitude.toFixed(6);
      latInput.value = latitude.toFixed(6);

      // reverse geocode → venue (if empty)
      locator.locationToAddress(WORLD_GEOCODER, { location: { type: "point", longitude, latitude } })
        .then(resp => {
          if (!venueInput.value) venueInput.value = resp.address || "";
        })
        .catch(() => {});

      // intersect with council land polygons
      civicLayer.queryFeatures({
        geometry: { type: "point", longitude, latitude },
        spatialRelationship: "intersects",
        returnGeometry: false,
        outFields: ["*"],
        num: 1
      }).then(res => {
        if (res.features && res.features.length) {
          const f = res.features[0];
          const attrs = f.attributes || {};
          const name =
            attrs.NAME || attrs.PARK_NAME || attrs.RESERVE_NAME || attrs.LABEL || "";

          fidInput.value   = attrs.OBJECTID || attrs.GlobalID || "";
          fnameInput.value = name;
          layerInput.value = civicLayer.title || "Council Land";

          if (name) venueInput.value = name;
        } else {
          fidInput.value = "";
          fnameInput.value = "";
          layerInput.value = "";
        }
      });
    }

    // click to choose
    view.on("click", (e) => {
      const { longitude, latitude } = e.mapPoint;
      setPoint(longitude, latitude);
    });

    // search result → drop marker
    search.on("select-result", (e) => {
      const geom = e.result.feature?.geometry || e.result.extent?.center;
      if (!geom) return;
      const { longitude, latitude } = geom;
      setPoint(longitude, latitude);
      view.goTo({ center: [longitude, latitude], zoom: 16 });
    });
  });
})();
