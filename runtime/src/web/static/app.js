const state = {
  currentView: "capture",
  inboxFilter: "all",
  selectedEntry: null,
  reviewEvents: [],
  editingSection: null,
  toastTimer: null,
  connection: {
    mode: "unknown",
    lanUrl: null,
    internetUrl: null,
  },
  voice: {
    active: false,
    recognition: null,
    requestId: null,
    baseText: "",
    statusTimer: null,
  },
  media: {
    clusters: [],
    current: null,
    draft: null,
    busy: false,
    uploadQueue: [],
    uploadBusy: false,
    uploadBatches: [],
    resumeBatch: null,
    contentRequests: [],
    contentDrafts: [],
  },
};

if ("serviceWorker" in navigator && window.isSecureContext) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => {
      // La aplicación sigue operativa en navegadores sin soporte PWA completo.
    });
  });
}

const mediaIntentLabels = {
  panoramica: "Panorámica",
  detalle: "Detalle",
  portada: "Portada",
  proceso: "Proceso",
  archivo: "Archivo",
  panoramica_paisaje: "Panorámica o paisaje",
  escena_general: "Escena general",
  grupo_aves: "Grupo de aves",
  retrato_detalle: "Retrato o detalle",
  accion_proceso: "Acción o proceso",
};

const mediaShotTypeLabels = {
  panoramica_paisaje: "Panorámica o paisaje",
  escena_general: "Escena general",
  grupo_aves: "Grupo de aves",
  retrato_detalle: "Retrato o detalle",
  accion_proceso: "Acción o proceso",
};

const mediaContentPillarLabels = {
  animales_y_personalidad: "Animales y personalidad",
  crianza_responsable: "Crianza responsable",
  vida_libre_y_naturaleza: "Vida libre y naturaleza",
  trabajo_y_profesionalismo: "Trabajo y profesionalismo",
  aprendizaje_y_educacion: "Aprendizaje y educación",
  razas_genetica_y_produccion: "Razas, genética y producción",
  productos_y_disponibilidad: "Productos y disponibilidad",
  comunidad_y_humor: "Comunidad y humor",
  fe_gratitud_y_proposito: "Fe, gratitud y propósito",
};

const mediaSubjectTagLabels = {
  pollitos: "Pollitos",
  gallinas_caseras: "Gallinas caseras",
  gallos: "Gallos",
  brahma: "Brahma",
  rhode_island_red: "Rhode Island Red",
  plymouth_rock_barred: "Plymouth Rock Barred",
  black_star: "Black Star",
  pastoreo: "Pastoreo",
  comportamiento_natural: "Comportamiento natural",
  alimentacion: "Alimentación",
  cuidado: "Cuidado",
  sanidad_con_contexto: "Sanidad con contexto",
  limpieza_e_infraestructura: "Limpieza e infraestructura",
  incubacion_y_cria: "Incubación y cría",
  naturaleza_y_paisaje: "Naturaleza y paisaje",
  trabajo_diario: "Trabajo diario",
};

const mediaDecisionLabels = {
  keep: "Conservar una favorita",
  reserve: "Reserva para contenido futuro",
  needs_context: "Falta contexto",
  private: "Privado, no publicar",
  no_usable: "Ninguna sirve",
};

const mediaSelectionReasonLabels = {
  mejor_encuadre: "Mejor encuadre",
  sujeto_mas_claro: "Sujeto más claro",
  cuenta_mejor_la_historia: "Cuenta mejor la historia",
  mejor_luz: "Mejor luz",
  mejor_gesto_o_comportamiento: "Mejor gesto o comportamiento",
  muestra_mejor_el_entorno: "Muestra mejor el entorno",
  representa_mejor_el_objetivo: "Representa mejor el objetivo",
  aporta_otro_angulo: "Aporta otro ángulo",
  mayor_valor_emocional: "Mayor valor emocional",
};

const facebookLaunchLabels = {
  facebook_portada: "Portada horizontal",
  facebook_bienvenida: "Bienvenida a Granja Luna",
  facebook_pollitos_caseros: "Pollitos caseros",
  facebook_brahma: "Brahma",
  facebook_black_star: "Proyecto Black Star",
  facebook_vida_natural: "Vida natural y cuidado",
  facebook_comunidad: "Abrir conversación",
};

const reviewStatusLabels = {
  pending: "Pendiente",
  validated: "Validada",
  needs_information: "Falta información",
  needs_correction: "A corregir",
  rejected: "Descartada",
};

const provenanceLabels = {
  predicted: "Predicho",
  extracted: "Extraído",
  calculated: "Calculado",
  suggested: "Sugerido",
  corrected: "Corregido",
  enriched: "Agregado",
  clarified: "Aclarado",
  missing: "No informado",
};

const correctionReasonHelp = {
  system_error: "El dato estaba en la entrada original, pero el sistema no lo detectó o lo interpretó mal.",
  new_information: "El dato no estaba mencionado en la entrada original y se agrega durante la revisión.",
  ambiguous_input: "La entrada era ambigua o contradictoria y se define una interpretación humana.",
};

const correctionReasonLabels = {
  system_error: "Error de detección",
  new_information: "Dato no mencionado",
  ambiguous_input: "Entrada ambigua",
  source_information_missing: "Información pendiente",
  correction_deferred: "Corrección postergada",
  system_limitation: "Limitación del sistema",
  human_validation: "Validación humana",
  not_relevant: "No corresponde",
};

const reviewSectionLabels = {
  purchase_general: "Datos generales",
  purchase_items: "Productos",
  classification: "Interpretación",
  review: "Revisión",
  curation: "Curaduría",
};

const trainingEligibilityLabels = {
  eligible: "Apto para extracción",
  not_for_extraction: "No usar para extracción",
  needs_review: "Requiere revisión",
  exclude: "Excluir del entrenamiento",
};

const intentOptions = [
  "registrar_compra",
  "registrar_venta_borrador",
  "registrar_movimiento_stock_borrador",
  "registrar_evento_sanitario_borrador",
  "registrar_bitacora_borrador",
  "crear_tarea_borrador",
  "analizar_existencias_reposicion",
  "analizar_decision_operativa",
  "preguntar_datos_faltantes",
  "preparar_reporte",
  "detectar_workflow_candidato",
];

const domainOptions = [
  "compras", "ventas", "stock-insumos", "sanidad", "incubacion", "infraestructura",
  "alimentacion", "reproductores", "tareas-mantenimiento", "reportes", "finanzas",
];

const eventLabels = {
  app_opened: "Aplicación abierta",
  inbox_created: "Entrada registrada",
  inbox_viewed: "Entrada revisada",
  inbox_corrected: "Corrección guardada",
  inbox_reviewed: "Revisión completada",
};

const eventIcons = {
  app_opened: "smartphone",
  inbox_created: "square-pen",
  inbox_viewed: "eye",
  inbox_corrected: "pencil",
  inbox_reviewed: "check-check",
};

document.addEventListener("DOMContentLoaded", () => {
  setToday();
  refreshIcons();
  bindNavigation();
  bindCaptureForm();
  bindInboxControls();
  bindActivityControls();
  bindOperationsControls();
  bindMediaControls();
  bindSheetControls();
  checkConnection();
  refreshInboxSummary();
  const requestedView = new URLSearchParams(window.location.search).get("view");
  if (["capture", "inbox", "activity", "operations", "media"].includes(requestedView) && requestedView !== "capture") {
    void switchView(requestedView);
  }
});

function refreshIcons() {
  if (window.lucide) window.lucide.createIcons({ attrs: { "aria-hidden": "true" } });
}

function setToday() {
  const label = new Intl.DateTimeFormat("es-PY", {
    weekday: "long", day: "numeric", month: "long",
  }).format(new Date());
  document.querySelector("#today-label").textContent = capitalize(label);
}

function capitalize(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : value;
}

function bindNavigation() {
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.target));
  });
}

async function switchView(target) {
  state.currentView = target;
  document.querySelectorAll(".view").forEach((view) => {
    const active = view.dataset.view === target;
    view.hidden = !active;
    view.classList.toggle("is-active", active);
  });
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.target === target);
  });
  if (target === "inbox") await loadInbox();
  if (target === "activity") await loadActivity();
  if (target === "operations") await loadOperations();
  if (target === "media") await loadContentWorkspace();
  window.scrollTo({ top: 0, behavior: "smooth" });
  refreshIcons();
}

function bindMediaControls() {
  document.querySelector("#refresh-media").addEventListener("click", loadContentWorkspace);
  document.querySelector("#media-upload-input").addEventListener("change", queueSelectedMedia);
  document.querySelector("#media-upload-form").addEventListener("submit", submitMediaUpload);
  document.querySelector("#content-request-form").addEventListener("submit", submitContentRequest);
  document.querySelectorAll("[data-connection-mode]").forEach((button) => {
    button.addEventListener("click", () => switchConnection(button.dataset.connectionMode));
  });
}

function renderConnectionSelector() {
  const { mode } = state.connection;
  const description = document.querySelector("#upload-connection-description");
  const note = document.querySelector("#upload-connection-note");
  if (!description || !note) return;
  if (mode === "lan") {
    description.textContent = "Directo a esta PC por Wi-Fi";
    note.textContent = "Ruta recomendada para fotos y videos grandes. No consume el túnel de Cloudflare.";
  } else if (mode === "internet") {
    description.textContent = "Vía Cloudflare Tunnel";
    note.textContent = "Funciona fuera de casa, pero las cargas grandes recorren Internet y pueden tardar más.";
  } else {
    description.textContent = "Ruta personalizada";
    note.textContent = "Podés elegir LAN para cargas locales o Internet para acceso remoto.";
  }
  if (document.documentElement.dataset.nativeShell === "true") {
    note.textContent += " En el APK, el cambio permanente también puede hacerse desde el botón de configuración.";
  }
  document.querySelectorAll("[data-connection-mode]").forEach((button) => {
    const selected = button.dataset.connectionMode === mode;
    const configured = button.dataset.connectionMode === "lan" ? state.connection.lanUrl : state.connection.internetUrl;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
    button.disabled = state.media.uploadBusy || !configured;
  });
}

function switchConnection(mode) {
  if (!["lan", "internet"].includes(mode)) return;
  if (state.media.uploadBusy) {
    showToast("Esperá a que termine la carga actual antes de cambiar de conexión");
    return;
  }
  if (mode === state.connection.mode) {
    showToast(mode === "lan" ? "Ya estás usando la LAN" : "Ya estás usando Internet");
    return;
  }
  const configured = mode === "lan" ? state.connection.lanUrl : state.connection.internetUrl;
  let target;
  try {
    target = new URL(configured);
    if (!["http:", "https:"].includes(target.protocol) || target.username || target.password) throw new Error();
  } catch (_error) {
    showToast("La conexión seleccionada no está configurada");
    return;
  }
  const hasUnsavedSelection = state.media.uploadQueue.length > 0 || document.querySelector("#media-upload-context").value.trim();
  if (hasUnsavedSelection && !window.confirm("Al cambiar de conexión tendrás que volver a elegir los archivos y copiar el contexto. ¿Continuar?")) return;
  target.pathname = "/";
  target.search = "";
  target.searchParams.set("view", "media");
  target.hash = "";
  window.location.assign(target.toString());
}

async function loadContentWorkspace() {
  await Promise.all([loadRecentUploads(), loadContentRequests(), loadContentDrafts(), loadMediaClusters()]);
}

async function loadContentDrafts() {
  const container = document.querySelector("#content-draft-list");
  try {
    state.media.contentDrafts = await api("/api/content/drafts?limit=12");
    renderContentDrafts();
  } catch (error) {
    container.innerHTML = `<p class="media-help">${escapeHtml(error.message)}</p>`;
  }
}

function renderContentDrafts() {
  const container = document.querySelector("#content-draft-list");
  if (!state.media.contentDrafts.length) {
    container.innerHTML = emptyMarkup("film", "Todavía no hay borradores locales para revisar.");
    refreshIcons();
    return;
  }
  container.innerHTML = state.media.contentDrafts.map((draft, index) => {
    const title = draft.filename.replace(/\.mp4$/i, "").replace(/^\d{4}-\d{2}-\d{2}-/, "").replaceAll("-", " ");
    return `<article class="content-draft-card">
      <video controls playsinline preload="${index === 0 ? "metadata" : "none"}" src="${escapeHtml(draft.media_url)}" aria-label="Vista previa de ${escapeHtml(title)}"></video>
      <div class="content-draft-copy">
        <header><div><span class="content-status-pill">Borrador local</span><h3>${escapeHtml(title)}</h3></div><i data-lucide="film"></i></header>
        <p>${formatFileSize(draft.size_bytes)} · ${formatDate(draft.updated_at, true)}</p>
        <small>No está publicado ni aprobado.</small>
      </div>
    </article>`;
  }).join("");
  const previews = [...container.querySelectorAll("video")];
  previews.forEach((preview) => {
    preview.addEventListener("play", () => {
      previews.forEach((other) => {
        if (other !== preview) other.pause();
      });
    });
  });
  refreshIcons();
}

function queueSelectedMedia(event) {
  const selected = [...(event.target.files || [])];
  const accepted = [];
  const rejected = [];
  let alreadySaved = 0;
  const resumeBatch = state.media.resumeBatch;
  const usedResumeItems = new Set(state.media.uploadQueue.map((item) => item.serverItemId).filter(Boolean));
  selected.forEach((file) => {
    const extensionOk = /\.(jpe?g|mp4)$/i.test(file.name);
    if (!extensionOk) {
      rejected.push(`${file.name}: tipo no admitido`);
      return;
    }
    if (!file.size) {
      rejected.push(`${file.name}: archivo vacío`);
      return;
    }
    if (file.size > 1024 * 1024 * 1024) {
      rejected.push(`${file.name}: supera 1 GB`);
      return;
    }
    const key = `${file.name}|${file.size}|${file.lastModified}`;
    if (state.media.uploadQueue.some((item) => item.key === key)) return;
    if (resumeBatch) {
      const serverItem = resumeBatch.items.find((item) => (
        !["uploaded", "duplicate"].includes(item.status)
        && !usedResumeItems.has(item.id)
        && item.original_name === file.name
        && Number(item.expected_size) === file.size
      ));
      if (serverItem) {
        usedResumeItems.add(serverItem.id);
        accepted.push({ key, file, serverItemId: serverItem.id, status: "pending", progress: 0, error: null });
        return;
      }
      const savedItem = resumeBatch.items.find((item) => (
        ["uploaded", "duplicate"].includes(item.status)
        && item.original_name === file.name
        && Number(item.expected_size) === file.size
      ));
      if (savedItem) {
        alreadySaved += 1;
        return;
      }
      rejected.push(`${file.name}: no pertenece a esta tanda pendiente`);
      return;
    }
    accepted.push({ key, file, status: "pending", progress: 0, error: null });
  });
  state.media.uploadQueue.push(...accepted);
  if (state.media.uploadQueue.length > 100) {
    state.media.uploadQueue = state.media.uploadQueue.slice(0, 100);
    rejected.push("La tanda admite hasta 100 archivos.");
  }
  event.target.value = "";
  renderMediaUploadQueue();
  if (accepted.length && resumeBatch) {
    showToast(`${accepted.length} pendiente${accepted.length === 1 ? "" : "s"} preparado${accepted.length === 1 ? "" : "s"}${alreadySaved ? `; ${alreadySaved} ya guardado${alreadySaved === 1 ? "" : "s"}` : ""}`);
  } else if (rejected.length) {
    showToast(rejected[0]);
  } else if (alreadySaved) {
    showToast("Esos archivos ya están guardados en la tanda");
  }
}

function renderMediaUploadQueue() {
  const container = document.querySelector("#media-upload-queue");
  const submit = document.querySelector("#media-upload-submit");
  const queue = state.media.uploadQueue;
  submit.disabled = !queue.length || state.media.uploadBusy;
  submit.innerHTML = state.media.resumeBatch
    ? '<i data-lucide="rotate-ccw"></i> Reanudar archivos pendientes'
    : '<i data-lucide="upload"></i> Guardar en la biblioteca';
  if (!queue.length) {
    container.innerHTML = state.media.resumeBatch ? `<div class="media-resume-banner">
      <div><strong>Reanudando la tanda interrumpida</strong><small>Elegí nuevamente los videos. Los ya guardados se omitirán.</small></div>
      <button type="button" data-cancel-resume>Cancelar</button>
    </div>` : "";
    container.querySelector("[data-cancel-resume]")?.addEventListener("click", cancelResumeMediaUpload);
    refreshIcons();
    return;
  }
  const total = queue.reduce((sum, item) => sum + item.file.size, 0);
  container.innerHTML = `${state.media.resumeBatch ? `<div class="media-resume-banner">
    <div><strong>Reanudando ${escapeHtml(state.media.resumeBatch.id)}</strong><small>Solo se enviarán los archivos pendientes que coincidan.</small></div>
    <button type="button" data-cancel-resume>Cancelar</button>
  </div>` : ""}<div class="media-upload-summary">${queue.length} archivo${queue.length === 1 ? "" : "s"} · ${formatFileSize(total)}</div>${queue.map((item, index) => `
    <div class="media-upload-row">
      <i data-lucide="${/\.mp4$/i.test(item.file.name) ? "video" : "image"}"></i>
      <div><strong>${escapeHtml(item.file.name)}</strong><small>${formatFileSize(item.file.size)} · ${mediaUploadStatusLabel(item.status)}${item.error ? ` · ${escapeHtml(item.error)}` : ""}</small></div>
      <button class="media-upload-remove" type="button" data-remove-upload="${index}" ${state.media.uploadBusy ? "disabled" : ""} aria-label="Quitar ${escapeHtml(item.file.name)}"><i data-lucide="x"></i></button>
    </div>`).join("")}`;
  container.querySelectorAll("[data-remove-upload]").forEach((button) => button.addEventListener("click", () => {
    state.media.uploadQueue.splice(Number(button.dataset.removeUpload), 1);
    renderMediaUploadQueue();
  }));
  container.querySelector("[data-cancel-resume]")?.addEventListener("click", cancelResumeMediaUpload);
  refreshIcons();
}

function startResumeMediaUpload(batchId) {
  if (state.media.uploadBusy) return;
  const batch = state.media.uploadBatches.find((item) => item.id === batchId);
  if (!batch) {
    showToast("No encontramos la tanda para reanudar");
    return;
  }
  if (state.media.uploadQueue.length && !window.confirm("La selección actual se reemplazará por la tanda interrumpida. ¿Continuar?")) return;
  state.media.resumeBatch = batch;
  state.media.uploadQueue = [];
  const context = document.querySelector("#media-upload-context");
  context.value = batch.context || "";
  context.disabled = true;
  renderMediaUploadQueue();
  document.querySelector("#media-upload-input").click();
}

function cancelResumeMediaUpload() {
  if (state.media.uploadBusy) return;
  state.media.resumeBatch = null;
  state.media.uploadQueue = [];
  const context = document.querySelector("#media-upload-context");
  context.disabled = false;
  context.value = "";
  renderMediaUploadQueue();
  showToast("Reanudación cancelada; la tanda sigue conservada");
}

async function submitMediaUpload(event) {
  event.preventDefault();
  if (!state.media.uploadQueue.length || state.media.uploadBusy) return;
  state.media.uploadBusy = true;
  renderConnectionSelector();
  state.media.uploadQueue.forEach((item) => { item.status = "pending"; item.error = null; item.progress = 0; });
  renderMediaUploadQueue();
  updateMediaUploadProgress(0, "Preparando la tanda…", false);
  const totalBytes = state.media.uploadQueue.reduce((sum, item) => sum + item.file.size, 0);
  let completedBytes = 0;
  let batch;
  try {
    if (state.media.resumeBatch) {
      batch = await api(`/api/media/upload-batches/${encodeURIComponent(state.media.resumeBatch.id)}`);
    } else {
      batch = await api("/api/media/upload-batches", {
        method: "POST",
        body: JSON.stringify({
          context: document.querySelector("#media-upload-context").value.trim() || null,
          files: state.media.uploadQueue.map((item) => ({
            name: item.file.name,
            size: item.file.size,
            type: item.file.type || "application/octet-stream",
            last_modified: item.file.lastModified,
          })),
        }),
      });
    }
    for (let index = 0; index < state.media.uploadQueue.length; index += 1) {
      const queued = state.media.uploadQueue[index];
      const serverItem = queued.serverItemId
        ? batch.items.find((item) => item.id === queued.serverItemId)
        : batch.items[index];
      if (!serverItem) throw new Error(`No se encontró ${queued.file.name} dentro de la tanda.`);
      queued.status = "uploading";
      renderMediaUploadQueue();
      try {
        const saved = await uploadMediaFile(batch.id, serverItem.id, queued.file, (loaded) => {
          queued.progress = loaded;
          const percent = totalBytes ? ((completedBytes + loaded) / totalBytes) * 100 : 0;
          updateMediaUploadProgress(percent, `Subiendo ${index + 1} de ${state.media.uploadQueue.length}…`, false);
        });
        queued.status = saved.status;
      } catch (error) {
        queued.status = "failed";
        queued.error = error.message;
      }
      completedBytes += queued.file.size;
      renderMediaUploadQueue();
    }
    const refreshed = await api(`/api/media/upload-batches/${encodeURIComponent(batch.id)}`);
    const unfinished = refreshed.items.filter((item) => !["uploaded", "duplicate", "failed"].includes(item.status));
    if (unfinished.length) {
      state.media.resumeBatch = refreshed;
      state.media.uploadQueue = [];
      renderMediaUploadReceipt(null, `${unfinished.length} archivo${unfinished.length === 1 ? " queda" : "s quedan"} pendiente${unfinished.length === 1 ? "" : "s"}. Podés reanudar nuevamente esta misma tanda.`);
      showToast("La tanda sigue disponible para reanudar");
      await loadRecentUploads();
      return;
    }
    updateMediaUploadProgress(100, "Inventariando el material…", false);
    const completed = await api(`/api/media/upload-batches/${encodeURIComponent(batch.id)}/complete`, { method: "POST" });
    renderMediaUploadReceipt(completed);
    const hasErrors = completed.error_count > 0;
    if (!hasErrors) {
      state.media.uploadQueue = [];
      document.querySelector("#media-upload-context").value = "";
      document.querySelector("#media-upload-context").disabled = false;
      state.media.resumeBatch = null;
    }
    showToast(hasErrors ? "La tanda terminó con archivos para revisar" : "Material guardado en la biblioteca");
    await Promise.all([loadRecentUploads(), loadMediaClusters()]);
  } catch (error) {
    renderMediaUploadReceipt(null, error.message);
    showToast(error.message || "No se pudo completar la carga");
  } finally {
    state.media.uploadBusy = false;
    renderConnectionSelector();
    updateMediaUploadProgress(100, "Carga finalizada", true);
    renderMediaUploadQueue();
  }
}

function uploadMediaFile(batchId, itemId, file, onProgress) {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("PUT", `/api/media/upload-batches/${encodeURIComponent(batchId)}/items/${encodeURIComponent(itemId)}`);
    request.setRequestHeader("Content-Type", file.type || "application/octet-stream");
    request.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) onProgress(Math.min(event.loaded, file.size));
    });
    request.addEventListener("load", () => {
      let payload = null;
      try { payload = JSON.parse(request.responseText); } catch (_error) { payload = null; }
      if (request.status >= 200 && request.status < 300) {
        resolve(payload);
        return;
      }
      const detail = payload?.detail;
      reject(new Error(typeof detail === "string" ? detail : detail?.message || `Error ${request.status}`));
    });
    request.addEventListener("error", () => reject(new Error("Se perdió la conexión durante la carga.")));
    request.addEventListener("abort", () => reject(new Error("Carga cancelada.")));
    request.send(file);
  });
}

function updateMediaUploadProgress(value, label, hide) {
  const panel = document.querySelector("#media-upload-progress");
  panel.hidden = hide;
  document.querySelector("#media-upload-progress-label").textContent = label;
  document.querySelector("#media-upload-progress-value").textContent = `${Math.round(value)}%`;
  document.querySelector("#media-upload-progress-bar").value = Math.max(0, Math.min(100, value));
}

function renderMediaUploadReceipt(batch, error = null) {
  const container = document.querySelector("#media-upload-receipt");
  if (error) {
    container.innerHTML = `<article class="media-upload-receipt"><h3>No se completó la tanda</h3><p>${escapeHtml(error)}</p></article>`;
    return;
  }
  if (!batch) {
    container.innerHTML = "";
    return;
  }
  container.innerHTML = `<article class="media-upload-receipt is-success"><h3>Material recibido</h3><p>${batch.uploaded_count} guardado${batch.uploaded_count === 1 ? "" : "s"}, ${batch.duplicate_count} duplicado${batch.duplicate_count === 1 ? "" : "s"} y ${batch.error_count} con error. El lote quedó identificado como ${escapeHtml(batch.id)}.</p></article>`;
}

async function loadRecentUploads() {
  const container = document.querySelector("#media-recent-uploads");
  try {
    state.media.uploadBatches = await api("/api/media/upload-batches?limit=6");
    renderRecentUploads();
    updateContentMediaOptions();
  } catch (error) {
    container.innerHTML = `<p class="media-help">${escapeHtml(error.message)}</p>`;
  }
}

function renderRecentUploads() {
  const container = document.querySelector("#media-recent-uploads");
  if (!state.media.uploadBatches.length) {
    container.innerHTML = "";
    return;
  }
  container.innerHTML = `<p class="eyebrow">Subidas recientes</p>${state.media.uploadBatches.map((batch) => {
    const retriable = batch.items.filter((item) => (
      ["pending", "uploading"].includes(item.status)
      || (item.status === "failed" && !String(item.error || "").startsWith("[cancelled_by_user]"))
    ));
    const alreadySaved = batch.items.filter((item) => ["uploaded", "duplicate"].includes(item.status)).length;
    return `
    <article class="recent-upload-card">
      <header><h3>${batch.expected_count} archivo${batch.expected_count === 1 ? "" : "s"} · ${formatFileSize(batch.expected_bytes)}</h3><span class="content-status-pill">${mediaUploadStatusLabel(batch.status)}</span></header>
      ${batch.context ? `<p>${escapeHtml(batch.context)}</p>` : ""}
      <ul class="recent-upload-files">${batch.items.slice(0, 5).map((item) => `<li>${escapeHtml(item.original_name)} · ${mediaUploadItemStatusLabel(item)}</li>`).join("")}${batch.items.length > 5 ? `<li>y ${batch.items.length - 5} más…</li>` : ""}</ul>
      ${retriable.length && ["pending", "uploading", "completed_with_errors"].includes(batch.status) ? `<div class="recent-upload-actions"><span>${alreadySaved} guardado${alreadySaved === 1 ? "" : "s"} · ${retriable.length} por reanudar</span><button type="button" data-resume-upload="${escapeHtml(batch.id)}">Reanudar</button></div>` : ""}
      <p>${formatDate(batch.created_at, true)} · ${escapeHtml(batch.id)}</p>
    </article>`;
  }).join("")}`;
  container.querySelectorAll("[data-resume-upload]").forEach((button) => {
    button.addEventListener("click", () => startResumeMediaUpload(button.dataset.resumeUpload));
  });
}

function updateContentMediaOptions() {
  const select = document.querySelector("#content-request-media");
  const current = select.value;
  const completed = state.media.uploadBatches.filter((batch) => ["completed", "completed_with_errors"].includes(batch.status));
  select.innerHTML = '<option value="">Sin tanda vinculada</option>' + completed.map((batch) => `<option value="${escapeHtml(batch.id)}">${formatDate(batch.created_at, true)} · ${batch.expected_count} archivo${batch.expected_count === 1 ? "" : "s"}</option>`).join("");
  if (completed.some((batch) => batch.id === current)) select.value = current;
}

async function submitContentRequest(event) {
  event.preventDefault();
  const submit = document.querySelector("#content-request-submit");
  const instruction = document.querySelector("#content-request-instruction").value.trim();
  if (!instruction) return;
  submit.disabled = true;
  const mediaBatchId = document.querySelector("#content-request-media").value;
  try {
    const request = await api("/api/content/requests", {
      method: "POST",
      body: JSON.stringify({
        instruction,
        content_type: document.querySelector("#content-request-type").value,
        channels: [document.querySelector("#content-request-channel").value].filter(Boolean),
        media_batch_ids: [mediaBatchId].filter(Boolean),
        objective: document.querySelector("#content-request-objective").value.trim() || null,
        audience: document.querySelector("#content-request-audience").value.trim() || null,
        source_stage: document.querySelector("#content-request-stage").value,
        call_to_action: document.querySelector("#content-request-cta").value.trim() || null,
      }),
    });
    document.querySelector("#content-request-result").innerHTML = renderContentRequestCard(request, true);
    document.querySelector("#content-request-instruction").value = "";
    state.media.contentRequests.unshift(request);
    renderContentRequests();
    showToast("Solicitud guardada en el Estudio");
  } catch (error) {
    showToast(error.message);
  } finally {
    submit.disabled = false;
    refreshIcons();
  }
}

async function loadContentRequests() {
  try {
    state.media.contentRequests = await api("/api/content/requests?limit=8");
    renderContentRequests();
  } catch (error) {
    document.querySelector("#content-request-list").innerHTML = `<p class="media-help">${escapeHtml(error.message)}</p>`;
  }
}

function renderContentRequests() {
  const container = document.querySelector("#content-request-list");
  if (!state.media.contentRequests.length) {
    container.innerHTML = "";
    return;
  }
  container.innerHTML = `<p class="eyebrow">Solicitudes recientes</p>${state.media.contentRequests.map((item) => renderContentRequestCard(item)).join("")}`;
}

function renderContentRequestCard(item, highlighted = false) {
  const questions = item.questions_to_resolve || [];
  const superseded = item.status === "superseded";
  return `<article class="content-request-card ${highlighted ? "is-highlighted" : ""}">
    <header><h3>${escapeHtml(item.instruction)}</h3><span class="content-status-pill">${superseded ? "Reemplazada" : "Idea registrada"}</span></header>
    <div class="content-request-meta"><span>${escapeHtml(item.content_type)}</span>${(item.channels || []).map((channel) => `<span>${escapeHtml(channel)}</span>`).join("")}<span>${item.media_batch_ids?.length || 0} tanda vinculada</span></div>
    <p>${superseded ? `Esta solicitud fue reemplazada por ${escapeHtml(item.superseded_by)} y se conserva como antecedente.` : "El agente todavía no generó una pieza: esta solicitud será la referencia trazable para brief, borrador y revisión."}</p>
    ${!superseded && questions.length ? `<ul class="content-question-list">${questions.slice(0, 5).map((question) => `<li>${escapeHtml(question.question)}</li>`).join("")}</ul>` : ""}
    <p>${formatDate(item.created_at, true)} · ${escapeHtml(item.id)}</p>
  </article>`;
}

function mediaUploadStatusLabel(status) {
  return ({ pending: "Pendiente", uploading: "Subiendo", uploaded: "Guardado", duplicate: "Duplicado", failed: "Error", completed: "Completada", completed_with_errors: "Con errores" })[status] || status;
}

function mediaUploadItemStatusLabel(item) {
  if (item.status === "failed" && String(item.error || "").startsWith("[cancelled_by_user]")) return "Omitido";
  return mediaUploadStatusLabel(item.status);
}

function formatFileSize(bytes) {
  const value = Number(bytes || 0);
  if (value < 1024) return `${value} B`;
  if (value < 1024 ** 2) return `${(value / 1024).toFixed(1)} KB`;
  if (value < 1024 ** 3) return `${(value / 1024 ** 2).toFixed(1)} MB`;
  return `${(value / 1024 ** 3).toFixed(2)} GB`;
}

async function loadMediaClusters() {
  const list = document.querySelector("#media-cluster-list");
  const workspace = document.querySelector("#media-curation-workspace");
  list.innerHTML = loadingMarkup("Cargando grupos");
  workspace.innerHTML = "";
  refreshIcons();
  try {
    state.media.clusters = await api("/api/media/clusters?limit=100");
    if (!state.media.clusters.length) {
      list.innerHTML = "";
      workspace.innerHTML = emptyMarkup("images", "Todavía no hay ráfagas para curar. Las cargas nuevas aparecen en el recibo de Subir material.");
      refreshIcons();
      return;
    }
    renderMediaClusterStrip();
    const preferred = state.media.current?.id && state.media.clusters.some((item) => item.id === state.media.current.id)
      ? state.media.current.id
      : state.media.clusters[0].id;
    await openMediaCluster(preferred);
  } catch (error) {
    list.innerHTML = "";
    workspace.innerHTML = errorMarkup(error.message);
  }
  refreshIcons();
}

function renderMediaClusterStrip() {
  const list = document.querySelector("#media-cluster-list");
  list.innerHTML = state.media.clusters.map((cluster, index) => {
    const selected = cluster.id === state.media.current?.id;
    const curated = Boolean(cluster.curation);
    return `<button class="media-cluster-chip ${selected ? "is-selected" : ""}" type="button" data-media-cluster="${escapeHtml(cluster.id)}">
      <span>${index + 1}</span><strong>${cluster.item_count} fotos</strong>${curated ? '<i data-lucide="check"></i>' : ""}
    </button>`;
  }).join("");
  list.querySelectorAll("[data-media-cluster]").forEach((button) => {
    button.addEventListener("click", () => openMediaCluster(button.dataset.mediaCluster));
  });
  refreshIcons();
}

async function openMediaCluster(clusterId) {
  const workspace = document.querySelector("#media-curation-workspace");
  workspace.innerHTML = loadingMarkup("Creando miniaturas y análisis técnico local");
  refreshIcons();
  try {
    let cluster = await api(`/api/media/clusters/${encodeURIComponent(clusterId)}`);
    if (cluster.members.some((item) => !item.thumbnail_url || item.brightness_mean == null)) {
      cluster = await api(`/api/media/clusters/${encodeURIComponent(clusterId)}/technical-analysis`, { method: "POST" });
    }
    state.media.current = cluster;
    state.media.clusters = state.media.clusters.map((item) => item.id === cluster.id ? cluster : item);
    state.media.draft = mediaDraftFromCluster(cluster);
    renderMediaClusterStrip();
    renderMediaWorkspace();
  } catch (error) {
    workspace.innerHTML = errorMarkup(error.message);
  }
  refreshIcons();
}

function mediaDraftFromCluster(cluster) {
  const saved = cluster.curation || {};
  return {
    shotTypes: [...(saved.shot_types || [])],
    contentPillars: [...(saved.content_pillars || [])],
    subjectTags: [...(saved.subject_tags || [])],
    groupDecision: saved.group_decision || "keep",
    primaryAssetId: saved.primary_asset_id || null,
    primaryShotType: saved.primary_shot_type || null,
    primaryReasons: [...(saved.primary_reasons || [])],
    primaryCampaignSlots: [...(saved.primary_campaign_slots || [])],
    secondaryAssetId: saved.secondary_asset_id || null,
    secondaryShotType: saved.secondary_shot_type || null,
    secondaryReasons: [...(saved.secondary_reasons || [])],
    secondaryCampaignSlots: [...(saved.secondary_campaign_slots || [])],
    note: saved.note || "",
  };
}

function renderMediaWorkspace() {
  const cluster = state.media.current;
  const draft = state.media.draft;
  if (!cluster || !draft) return;
  const coverage = new Set(state.media.clusters.flatMap((item) => item.curation?.campaign_slots || []));
  const curatedCount = state.media.clusters.filter((item) => item.curation).length;
  const coverageItems = Object.entries(facebookLaunchLabels).map(([value, label]) => `
    <li class="${coverage.has(value) ? "is-covered" : ""}"><i data-lucide="${coverage.has(value) ? "circle-check" : "circle-dashed"}"></i><span>${escapeHtml(label)}</span></li>`).join("");
  const cards = cluster.members.map((member, index) => renderMediaAssetCard(member, index, draft)).join("");
  document.querySelector("#media-curation-workspace").innerHTML = `
    <section class="facebook-mission-card">
      <div><p class="eyebrow">Biblioteca editorial</p><h2>Conocer todo el material real</h2><p>Curamos cada grupo por su valor presente o futuro. La selección final de Facebook se hará después de conocer la biblioteca completa.</p></div>
      <strong>${curatedCount}/${state.media.clusters.length} revisados</strong>
      <details><summary>Campaña inicial de Facebook · ${coverage.size}/7 usos cubiertos</summary><ul class="launch-coverage">${coverageItems}</ul></details>
    </section>
    <section class="media-review-panel">
      <div class="section-heading-row"><div><p class="eyebrow">Ráfaga ${escapeHtml(cluster.label.replace("Rafaga ", ""))}</p><h2>1. Mirá las tomas</h2></div><span class="information-badge">${cluster.members.length} candidatas</span></div>
      <p class="media-help">Tocá una imagen para verla ampliada. La miniatura no alcanza para juzgar nitidez o encuadre fino; Gemini puede aportar esa revisión visual.</p>
      <div class="media-grid">${cards}</div>
    </section>
    <section class="media-review-panel media-curation-form">
      <h2>2. Contanos qué sabés</h2>
      <p class="media-help">Tu mayor aporte es el contexto real. Marcá sólo lo que conozcas; Gemini puede sugerir la lectura visual.</p>
      <fieldset><legend>Qué aparece o qué estaba ocurriendo</legend><div class="media-check-grid">${renderMediaChecks(mediaSubjectTagLabels, "media-subject", draft.subjectTags)}</div></fieldset>
      <fieldset><legend>Qué historia podría ayudar a contar</legend><div class="media-check-grid">${renderMediaChecks(mediaContentPillarLabels, "media-pillar", draft.contentPillars)}</div></fieldset>
      <fieldset><legend>Tipo de toma, si resulta claro</legend><div class="media-check-grid">${renderMediaChecks(mediaShotTypeLabels, "media-shot-type", draft.shotTypes)}</div></fieldset>
      <label>Contexto humano<textarea id="media-curation-note" rows="4" placeholder="Ej.: eran pollitos caseros de primeras semanas; la intención era mostrar el manejo general; evitar el foco visible por percepción de cercanía.">${escapeHtml(draft.note)}</textarea></label>
      <div class="media-actions media-context-actions"><button class="gemini-button" id="analyze-media-gemini" type="button"><i data-lucide="sparkles"></i> Analizar con Gemini</button></div>
      <p class="external-processing-hint">Gemini recibirá copias reducidas sin EXIF, nunca los originales. No publica ni confirma tu selección.</p>
    </section>
    <section id="media-gemini-result">${renderGeminiMediaResult(cluster.gemini_analysis)}</section>
    <section class="media-review-panel media-curation-form">
      <h2>3. Registrá tu decisión</h2>
      <p class="media-help">Tu elección puede ser intuitiva. Los motivos son rápidos y opcionales; una foto no elegida no queda descartada.</p>
      <label>Decisión del grupo<select id="media-group-decision">${Object.entries(mediaDecisionLabels).map(([value, label]) => `<option value="${value}" ${draft.groupDecision === value ? "selected" : ""}>${label}</option>`).join("")}</select></label>
      ${renderFavoriteEditor("primary", draft)}
      ${renderFavoriteEditor("secondary", draft)}
      <div class="media-actions"><button class="primary-button" id="save-media-curation" type="button"><i data-lucide="save"></i> Guardar curaduría</button></div>
    </section>
    <dialog class="media-preview-dialog" id="media-preview-dialog"><button type="button" id="close-media-preview" aria-label="Cerrar vista ampliada"><i data-lucide="x"></i></button><img id="media-preview-image" alt="Vista ampliada de la candidata"><p id="media-preview-caption"></p></dialog>`;
  bindMediaWorkspaceControls();
  refreshIcons();
}

function renderMediaChecks(labels, name, selected) {
  return Object.entries(labels).map(([value, label]) => `
    <label class="media-check"><input type="checkbox" name="${name}" value="${value}" ${selected.includes(value) ? "checked" : ""}><span>${escapeHtml(label)}</span></label>`).join("");
}

function renderMediaAssetCard(member, index, draft) {
  const primary = member.id === draft.primaryAssetId;
  const secondary = member.id === draft.secondaryAssetId;
  return `<article class="media-asset-card ${primary ? "is-primary" : ""} ${secondary ? "is-secondary" : ""}">
    <button class="media-image-wrap" type="button" data-media-preview="${escapeHtml(member.preview_url || member.thumbnail_url)}" data-media-caption="Foto ${index + 1} · ${escapeHtml(member.original_name)}"><img src="${escapeHtml(member.thumbnail_url)}" alt="Candidata ${index + 1}" loading="lazy"><span>${index + 1}</span><small><i data-lucide="maximize-2"></i> Ver grande</small></button>
    <div class="media-asset-body"><strong>${escapeHtml(member.original_name)}</strong>
      <div class="media-local-signals">${renderMediaLocalSignals(member, index, state.media.current.members)}</div>
      <div class="favorite-buttons"><button type="button" data-media-favorite="primary" data-asset-id="${escapeHtml(member.id)}" class="${primary ? "is-selected" : ""}">Principal</button><button type="button" data-media-favorite="secondary" data-asset-id="${escapeHtml(member.id)}" class="${secondary ? "is-selected" : ""}">Secundaria</button></div>
    </div>
  </article>`;
}

function renderMediaLocalSignals(member, index, members) {
  const orientation = member.width > member.height ? "Horizontal" : member.width < member.height ? "Vertical" : "Cuadrada";
  const similarIndex = members.findIndex((candidate, candidateIndex) => candidateIndex !== index && perceptualHashDistance(member.perceptual_hash, candidate.perceptual_hash) <= 2);
  const warnings = (member.warnings || []).map((warning) => `<span class="is-warning">${escapeHtml(formatPlainToken(warning))}</span>`);
  return [`<span>${orientation}</span>`, similarIndex >= 0 ? `<span>Muy similar a foto ${similarIndex + 1}</span>` : "", ...warnings].filter(Boolean).join("");
}

function perceptualHashDistance(first, second) {
  if (!first || !second) return Number.POSITIVE_INFINITY;
  try {
    let value = BigInt(`0x${first}`) ^ BigInt(`0x${second}`);
    let distance = 0;
    while (value) {
      distance += Number(value & 1n);
      value >>= 1n;
    }
    return distance;
  } catch (_error) {
    return Number.POSITIVE_INFINITY;
  }
}

function renderFavoriteEditor(role, draft) {
  const isPrimary = role === "primary";
  const assetId = isPrimary ? draft.primaryAssetId : draft.secondaryAssetId;
  if (!assetId) return `<div class="media-favorite-empty">${isPrimary ? "Elegí una principal en las fotos, o indicá que ninguna sirve." : "La secundaria es opcional y sólo se usa cuando aporta otro ángulo o historia."}</div>`;
  const memberIndex = state.media.current.members.findIndex((item) => item.id === assetId);
  const shotType = isPrimary ? draft.primaryShotType : draft.secondaryShotType;
  const reasons = isPrimary ? draft.primaryReasons : draft.secondaryReasons;
  const campaignSlots = isPrimary ? draft.primaryCampaignSlots : draft.secondaryCampaignSlots;
  const title = isPrimary ? "Principal" : "Secundaria";
  return `<section class="media-favorite-editor">
    <h3>${title} · Foto ${memberIndex + 1}</h3>
    <label>Tipo de toma<select id="media-${role}-shot-type"><option value="">Dejar que Gemini sugiera</option>${Object.entries(mediaShotTypeLabels).map(([value, label]) => `<option value="${value}" ${shotType === value ? "selected" : ""}>${label}</option>`).join("")}</select></label>
    <fieldset><legend>¿Por qué la preferís? · opcional</legend><div class="media-check-grid">${renderMediaChecks(mediaSelectionReasonLabels, `media-${role}-reason`, reasons)}</div></fieldset>
    <details><summary>¿Podría servir para el lanzamiento de Facebook?</summary><div class="media-check-grid media-campaign-checks">${renderMediaChecks(facebookLaunchLabels, `media-${role}-campaign`, campaignSlots)}</div></details>
  </section>`;
}

function bindMediaWorkspaceControls() {
  document.querySelectorAll("[data-media-favorite]").forEach((button) => button.addEventListener("click", () => {
    captureMediaDraft();
    const role = button.dataset.mediaFavorite;
    const assetId = button.dataset.assetId;
    if (role === "primary") {
      state.media.draft.primaryAssetId = state.media.draft.primaryAssetId === assetId ? null : assetId;
      if (!state.media.draft.primaryAssetId) {
        state.media.draft.primaryShotType = null;
        state.media.draft.primaryReasons = [];
        state.media.draft.primaryCampaignSlots = [];
        state.media.draft.secondaryAssetId = null;
      } else {
        state.media.draft.groupDecision = "keep";
      }
      if (state.media.draft.secondaryAssetId === assetId) {
        state.media.draft.secondaryAssetId = null;
        state.media.draft.secondaryShotType = null;
        state.media.draft.secondaryReasons = [];
        state.media.draft.secondaryCampaignSlots = [];
      }
    } else {
      if (!state.media.draft.primaryAssetId) {
        showToast("Elegí primero una foto principal.");
        return;
      }
      if (state.media.draft.primaryAssetId === assetId) {
        showToast("Esa foto ya es la principal.");
        return;
      }
      state.media.draft.secondaryAssetId = state.media.draft.secondaryAssetId === assetId ? null : assetId;
      if (!state.media.draft.secondaryAssetId) {
        state.media.draft.secondaryShotType = null;
        state.media.draft.secondaryReasons = [];
        state.media.draft.secondaryCampaignSlots = [];
      }
    }
    renderMediaWorkspace();
  }));
  document.querySelectorAll("[data-media-preview]").forEach((button) => button.addEventListener("click", () => {
    const dialog = document.querySelector("#media-preview-dialog");
    document.querySelector("#media-preview-image").src = button.dataset.mediaPreview;
    document.querySelector("#media-preview-caption").textContent = button.dataset.mediaCaption;
    dialog.showModal();
  }));
  document.querySelector("#close-media-preview").addEventListener("click", () => document.querySelector("#media-preview-dialog").close());
  document.querySelector("#media-group-decision").addEventListener("change", (event) => {
    captureMediaDraft();
    state.media.draft.groupDecision = event.target.value;
    if (event.target.value === "no_usable") {
      state.media.draft.primaryAssetId = null;
      state.media.draft.secondaryAssetId = null;
      state.media.draft.primaryShotType = null;
      state.media.draft.secondaryShotType = null;
      state.media.draft.primaryReasons = [];
      state.media.draft.secondaryReasons = [];
      state.media.draft.primaryCampaignSlots = [];
      state.media.draft.secondaryCampaignSlots = [];
    }
    renderMediaWorkspace();
  });
  document.querySelector("#save-media-curation").addEventListener("click", saveMediaCuration);
  document.querySelector("#analyze-media-gemini").addEventListener("click", analyzeCurrentMediaWithGemini);
  document.querySelector("#apply-gemini-media-tags")?.addEventListener("click", applyGeminiMediaTags);
}

function captureMediaDraft() {
  const draft = state.media.draft;
  draft.shotTypes = [...document.querySelectorAll('input[name="media-shot-type"]:checked')].map((item) => item.value);
  draft.contentPillars = [...document.querySelectorAll('input[name="media-pillar"]:checked')].map((item) => item.value);
  draft.subjectTags = [...document.querySelectorAll('input[name="media-subject"]:checked')].map((item) => item.value);
  draft.groupDecision = document.querySelector("#media-group-decision")?.value || draft.groupDecision || "keep";
  draft.primaryShotType = document.querySelector("#media-primary-shot-type")?.value || null;
  draft.secondaryShotType = document.querySelector("#media-secondary-shot-type")?.value || null;
  draft.primaryReasons = [...document.querySelectorAll('input[name="media-primary-reason"]:checked')].map((item) => item.value);
  draft.secondaryReasons = [...document.querySelectorAll('input[name="media-secondary-reason"]:checked')].map((item) => item.value);
  draft.primaryCampaignSlots = [...document.querySelectorAll('input[name="media-primary-campaign"]:checked')].map((item) => item.value);
  draft.secondaryCampaignSlots = [...document.querySelectorAll('input[name="media-secondary-campaign"]:checked')].map((item) => item.value);
  [draft.primaryShotType, draft.secondaryShotType].filter(Boolean).forEach((value) => {
    if (!draft.shotTypes.includes(value)) draft.shotTypes.push(value);
  });
  draft.note = document.querySelector("#media-curation-note")?.value || "";
}

async function saveMediaCuration() {
  captureMediaDraft();
  const draft = state.media.draft;
  if (draft.groupDecision === "keep" && !draft.primaryAssetId) {
    showToast("Elegí una principal o indicá otra decisión para el grupo.");
    return;
  }
  try {
    const curation = await api(`/api/media/clusters/${encodeURIComponent(state.media.current.id)}/curation`, {
      method: "PATCH",
      body: JSON.stringify({
        shot_types: draft.shotTypes,
        content_pillars: draft.contentPillars,
        subject_tags: draft.subjectTags,
        group_decision: draft.groupDecision,
        primary_asset_id: draft.primaryAssetId,
        primary_shot_type: draft.primaryShotType,
        primary_reasons: draft.primaryReasons,
        primary_campaign_slots: draft.primaryCampaignSlots,
        secondary_asset_id: draft.secondaryAssetId,
        secondary_shot_type: draft.secondaryAssetId ? draft.secondaryShotType : null,
        secondary_reasons: draft.secondaryAssetId ? draft.secondaryReasons : [],
        secondary_campaign_slots: draft.secondaryAssetId ? draft.secondaryCampaignSlots : [],
        note: draft.note || null,
      }),
    });
    state.media.current.curation = curation;
    state.media.clusters = state.media.clusters.map((item) => item.id === state.media.current.id ? state.media.current : item);
    state.media.draft = mediaDraftFromCluster(state.media.current);
    showToast("Curaduría guardada en la biblioteca");
    renderMediaClusterStrip();
    renderMediaWorkspace();
  } catch (error) {
    showToast(error.message);
  }
}

async function analyzeCurrentMediaWithGemini() {
  captureMediaDraft();
  const draft = state.media.draft;
  if (!window.confirm("Confirmá que revisaste el grupo y no contiene personas sin autorización ni datos sensibles. Se enviarán a Gemini sólo copias reducidas sin EXIF; los originales permanecerán locales. ¿Continuar?")) return;
  const button = document.querySelector("#analyze-media-gemini");
  const result = document.querySelector("#media-gemini-result");
  button.disabled = true;
  result.innerHTML = loadingMarkup("Gemini está comparando las fotos según tu objetivo");
  refreshIcons();
  try {
    const stored = await api(`/api/media/clusters/${encodeURIComponent(state.media.current.id)}/gemini`, {
      method: "POST",
      body: JSON.stringify({
        shot_types: draft.shotTypes,
        content_pillars: draft.contentPillars,
        subject_tags: draft.subjectTags,
        campaign_slots: [...new Set([...draft.primaryCampaignSlots, ...draft.secondaryCampaignSlots])],
        context: draft.note || null,
        confirm_external_processing: true,
        confirm_privacy_review: true,
      }),
    });
    state.media.current.gemini_analysis = stored;
    state.media.clusters = state.media.clusters.map((item) => item.id === state.media.current.id ? state.media.current : item);
    showToast("Análisis de Gemini recibido");
    renderMediaWorkspace();
  } catch (error) {
    result.innerHTML = errorMarkup(error.message);
  } finally {
    button.disabled = false;
    refreshIcons();
  }
}

function renderGeminiMediaResult(stored) {
  const output = stored?.result;
  const analysis = output?.analysis;
  if (!analysis) return '<div class="gemini-empty"><i data-lucide="sparkles"></i><p>Gemini todavía no analizó este grupo.</p></div>';
  const validation = output.semantic_validation;
  const validationErrors = (validation?.errors || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const favorites = (analysis.favoritos_por_intencion || []).map((item) => `<li><strong>${escapeHtml(formatPlainToken(item.prioridad))}: ${escapeHtml(item.archivo)}</strong><span>${escapeHtml(mediaIntentLabels[item.intencion] || item.intencion)} · ${escapeHtml(item.motivo)}</span></li>`).join("");
  const risks = (analysis.riesgos || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const claims = (analysis.afirmaciones_que_requieren_verificacion || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const suggestions = analysis.etiquetas_sugeridas || {};
  const suggestedLabels = [...(suggestions.tipos_de_toma || []), ...(suggestions.temas || []), ...(suggestions.pilares || [])];
  const tagMarkup = suggestedLabels.map((value) => `<span>${escapeHtml(mediaShotTypeLabels[value] || mediaSubjectTagLabels[value] || mediaContentPillarLabels[value] || formatPlainToken(value))}</span>`).join("");
  const ranking = (analysis.ranking || []).map((item) => `<li><strong>${escapeHtml(item.archivo)} · ${escapeHtml(String(item.puntaje_1_a_5))}/5</strong><span>${escapeHtml(item.motivo)}</span>${item.problemas_visibles?.length ? `<small>${escapeHtml(item.problemas_visibles.join(" · "))}</small>` : ""}</li>`).join("");
  const differences = (analysis.diferencias_decisivas || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  const validationWarning = validation && !validation.valid ? `<div class="media-gemini-warning"><strong>Resultado no aplicable automáticamente</strong><ul>${validationErrors}</ul></div>` : "";
  const canApplySuggestions = validation?.valid === true;
  return `<article class="gemini-result-card"><div class="section-heading-row"><div><p class="eyebrow">Sugerencia externa</p><h2>Análisis de Gemini</h2></div><span class="information-badge">Requiere revisión</span></div>${validationWarning}<p>${escapeHtml(analysis.resumen_de_la_escena || "Comparación completada")}</p>${analysis.sin_candidata_adecuada ? '<p class="media-gemini-warning">Gemini no encontró una candidata suficientemente adecuada.</p>' : ""}${favorites ? `<ol>${favorites}</ol>` : ""}${tagMarkup ? `<div class="gemini-suggested-tags">${tagMarkup}</div>${canApplySuggestions ? '<button class="secondary-button" id="apply-gemini-media-tags" type="button">Agregar etiquetas sugeridas</button>' : ""}` : ""}${ranking ? `<details><summary>Ver comparación técnica y editorial</summary><ol>${ranking}</ol></details>` : ""}${differences ? `<details><summary>Diferencias decisivas</summary><ul>${differences}</ul></details>` : ""}${risks ? `<details><summary>Riesgos sugeridos</summary><ul>${risks}</ul></details>` : ""}${claims ? `<details><summary>Afirmaciones que necesitan verificación</summary><ul>${claims}</ul></details>` : ""}<p class="media-help">Gemini aporta lectura visual. Vos confirmás el contexto, la selección y cualquier afirmación pública.</p></article>`;
}

function applyGeminiMediaTags() {
  captureMediaDraft();
  if (state.media.current.gemini_analysis?.result?.semantic_validation?.valid !== true) {
    showToast("Este resultado no superó la validación y no puede aplicar etiquetas.");
    return;
  }
  const suggestions = state.media.current.gemini_analysis?.result?.analysis?.etiquetas_sugeridas || {};
  state.media.draft.shotTypes = [...new Set([...state.media.draft.shotTypes, ...(suggestions.tipos_de_toma || [])])];
  state.media.draft.subjectTags = [...new Set([...state.media.draft.subjectTags, ...(suggestions.temas || [])])];
  state.media.draft.contentPillars = [...new Set([...state.media.draft.contentPillars, ...(suggestions.pilares || [])])];
  showToast("Etiquetas de Gemini agregadas como borrador");
  renderMediaWorkspace();
}

function bindOperationsControls() {
  document.querySelector("#refresh-operations").addEventListener("click", loadOperations);
  document.querySelector("#brooding-area-form").addEventListener("submit", (event) => submitBroodingDraft(event, "area"));
  document.querySelector("#brooding-batch-form").addEventListener("submit", (event) => submitBroodingDraft(event, "batch"));
  document.querySelector("#brooding-event-form").addEventListener("submit", (event) => submitBroodingDraft(event, "event"));
}

async function loadOperations() {
  const batchesContainer = document.querySelector("#brooding-batches");
  const eggLotsContainer = document.querySelector("#egg-storage-lots");
  const pendingContainer = document.querySelector("#farm-pending-list");
  batchesContainer.innerHTML = loadingMarkup("Cargando lotes de cría");
  eggLotsContainer.innerHTML = loadingMarkup("Cargando huevos almacenados");
  pendingContainer.innerHTML = loadingMarkup("Cargando borradores");
  refreshIcons();
  try {
    const [areas, batches, incubationBatches, eggStorageAreas, eggLots, movementDrafts, structureDrafts, incubationDrafts, broodingDrafts] = await Promise.all([
      api("/api/operations/brooding/areas"),
      api("/api/operations/brooding/batches"),
      api("/api/operations/incubation/batches"),
      api("/api/operations/egg-storage/areas"),
      api("/api/operations/egg-storage/lots"),
      api("/api/operations/movements?status=awaiting_confirmation&limit=100"),
      api("/api/operations/structure/pending"),
      api("/api/operations/incubation/pending"),
      api("/api/operations/brooding/pending"),
    ]);
    const [batchDetails, incubationDetails] = await Promise.all([
      Promise.all(batches.map((item) => api(`/api/operations/brooding/batches/${encodeURIComponent(item.id)}`))),
      Promise.all(incubationBatches.map((item) => api(`/api/operations/incubation/batches/${encodeURIComponent(item.id)}`))),
    ]);
    renderBroodingOperation(areas, batchDetails, incubationDetails);
    renderEggStorage(eggStorageAreas, eggLots);
    renderFarmPending([
      ...movementDrafts.map((item) => ({ ...item, namespace: "movements" })),
      ...structureDrafts.map((item) => ({ ...item, namespace: "structure" })),
      ...incubationDrafts.map((item) => ({ ...item, namespace: "incubation" })),
      ...broodingDrafts.map((item) => ({ ...item, namespace: "brooding" })),
    ]);
  } catch (error) {
    batchesContainer.innerHTML = errorMarkup(error.message);
    eggLotsContainer.innerHTML = errorMarkup(error.message);
    pendingContainer.innerHTML = errorMarkup(error.message);
  }
  refreshIcons();
}

function renderEggStorage(areas, lots) {
  const available = lots.reduce((total, item) => total + Number(item.quantity_available || 0), 0);
  document.querySelector("#egg-storage-summary").innerHTML = `
    <div><span>Almacenes</span><strong>${areas.length}</strong></div>
    <div><span>Lotes</span><strong>${lots.length}</strong></div>
    <div><span>Disponibles</span><strong>${available}</strong></div>`;
  document.querySelector("#egg-storage-lots").innerHTML = lots.length
    ? lots.map((item) => `<article class="operation-card"><div class="entry-card-top"><span class="status-badge status-validated">${item.quantity_available} disponibles</span><time>${formatDateOnly(item.effective_date)}</time></div><h3>${escapeHtml(item.storage_area_name || item.storage_area_id)}</h3><p>${item.quantity_collected} recolectados · ${item.quantity_allocated} asignados · ${item.physical_separation ? "separados físicamente" : "almacenados juntos"}</p></article>`).join("")
    : emptyMarkup("egg", "Todavía no hay huevos almacenados confirmados");
}

function renderBroodingOperation(areas, batches, incubationBatches) {
  const active = batches.filter((item) => !item.summary.closed);
  const chicks = active.reduce((total, item) => total + Number(item.summary.current_count || 0), 0);
  document.querySelector("#brooding-summary").innerHTML = `
    <div><span>Zonas</span><strong>${areas.length}</strong></div>
    <div><span>Lotes activos</span><strong>${active.length}</strong></div>
    <div><span>Pollitos actuales</span><strong>${chicks}</strong></div>`;
  document.querySelector("#brooding-batches").innerHTML = batches.length
    ? batches.map((item) => `<article class="operation-card"><div class="entry-card-top"><span class="status-badge status-${item.summary.closed ? "validated" : "pending"}">${item.summary.closed ? "Cerrado" : "Activo"}</span><time>${formatDateOnly(item.data.start_date)}</time></div><h3>${escapeHtml(item.data.source_description)}</h3><p>${item.summary.current_count} actuales · ${item.summary.mortality} bajas · ${item.summary.transferred_out} trasladados</p></article>`).join("")
    : emptyMarkup("egg", "Todavía no hay lotes de cría confirmados");
  document.querySelector("#brooding-area-select").innerHTML = areas.length
    ? areas.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.data.name)}</option>`).join("")
    : '<option value="">Primero crea una zona</option>';
  document.querySelector("#brooding-batch-select").innerHTML = active.length
    ? active.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.data.source_description)} · ${item.summary.current_count}</option>`).join("")
    : '<option value="">No hay lotes activos</option>';
  const closedIncubation = incubationBatches.filter((item) => item.summary.closed);
  document.querySelector("#brooding-source-select").innerHTML = '<option value="">Sin vínculo</option>' + closedIncubation.map((item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.data.source_description)} · ${item.summary.results?.hatched_alive ?? 0} nacidos</option>`).join("");
}

function renderFarmPending(items) {
  const container = document.querySelector("#farm-pending-list");
  if (!items.length) {
    container.innerHTML = emptyMarkup("check-check", "No hay borradores pendientes");
    return;
  }
  container.innerHTML = items.map((item) => `<article class="operation-card"><div class="entry-card-top"><span class="status-badge status-pending">${formatToken(item.namespace)}</span><code>${escapeHtml(item.confirmation.code)}</code></div><h3>${escapeHtml(item.confirmation.summary)}</h3><div class="operation-actions"><button type="button" data-draft-action="confirm" data-namespace="${escapeHtml(item.namespace)}" data-id="${escapeHtml(item.id)}" data-code="${escapeHtml(item.confirmation.code)}">Confirmar</button><button class="secondary-button" type="button" data-draft-action="cancel" data-namespace="${escapeHtml(item.namespace)}" data-id="${escapeHtml(item.id)}" data-code="${escapeHtml(item.confirmation.code)}">Cancelar borrador</button></div></article>`).join("");
  container.querySelectorAll("[data-draft-action]").forEach((button) => button.addEventListener("click", () => actOnFarmDraft(button)));
}

async function actOnFarmDraft(button) {
  const action = button.dataset.draftAction;
  const card = button.closest(".operation-card");
  const summary = card.querySelector("h3").textContent;
  let reason = "";
  if (action === "confirm" && !window.confirm(`Confirmar exactamente:\n${summary}`)) return;
  if (action === "cancel") {
    reason = window.prompt(`Motivo para cancelar:\n${summary}`)?.trim() || "";
    if (!reason || !window.confirm("La cancelación quedará registrada en el historial. ¿Continuar?")) return;
  }
  button.disabled = true;
  try {
    await api(`/api/operations/${button.dataset.namespace}/${encodeURIComponent(button.dataset.id)}/${action}`, {
      method: "POST",
      body: JSON.stringify({
        confirmation_code: button.dataset.code,
        explicit_confirmation: true,
        ...(reason ? { reason } : {}),
      }),
    });
    showToast(action === "confirm" ? "Registro confirmado" : "Borrador cancelado");
    await loadOperations();
  } catch (error) {
    button.disabled = false;
    showToast(error.message);
  }
}

async function submitBroodingDraft(event, recordType) {
  event.preventDefault();
  const form = event.currentTarget;
  const submit = form.querySelector('button[type="submit"]');
  const payload = Object.fromEntries(new FormData(form).entries());
  ["capacity", "chicks_received", "age_min_days", "age_max_days", "quantity", "final_count"].forEach((field) => {
    if (payload[field] !== undefined && payload[field] !== "") payload[field] = Number(payload[field]);
  });
  Object.keys(payload).forEach((field) => {
    if (payload[field] === "") delete payload[field];
  });
  submit.disabled = true;
  try {
    const draft = await api(`/api/operations/brooding/${recordType}/drafts`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    showToast(`Borrador preparado: ${draft.confirmation.summary}`);
    form.reset();
    await loadOperations();
  } catch (error) {
    showToast(error.message);
  } finally {
    submit.disabled = false;
  }
}

function bindCaptureForm() {
  const form = document.querySelector("#capture-form");
  const message = document.querySelector("#message");
  message.addEventListener("input", updateComposerState);
  message.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
    event.preventDefault();
    if (!document.querySelector("#capture-submit").disabled) form.requestSubmit();
  });
  form.addEventListener("submit", captureEntry);
  bindVoiceInput();
  updateComposerState();
}

async function captureEntry(event) {
  event.preventDefault();
  const message = document.querySelector("#message");
  const context = document.querySelector("#context");
  const submit = document.querySelector("#capture-submit");
  const voiceButton = document.querySelector("#voice-button");
  const originalMessage = message.value.trim();
  const originalContext = context.value.trim();
  if (!originalMessage) return;
  if (state.voice.active) cancelVoiceInput();
  appendUserMessage(originalMessage);
  const pendingMessage = appendPendingAssistantMessage();
  submit.dataset.busy = "true";
  message.disabled = true;
  voiceButton.disabled = true;
  message.value = "";
  updateComposerState();
  refreshIcons();
  try {
    const entry = await api("/api/inbox", {
      method: "POST",
      body: JSON.stringify({ message: originalMessage, context: originalContext || null }),
    });
    renderCaptureResult(entry, pendingMessage);
    context.value = "";
    document.querySelector(".composer-context").open = false;
    showToast("Entrada guardada en el inbox");
    await refreshInboxSummary();
  } catch (error) {
    renderCaptureError(pendingMessage, error.message || "No se pudo guardar la entrada");
    message.value = originalMessage;
    showToast(error.message || "No se pudo guardar la entrada");
  } finally {
    delete submit.dataset.busy;
    message.disabled = false;
    voiceButton.disabled = false;
    updateComposerState();
    refreshIcons();
    message.focus();
    scrollChatToEnd();
  }
}

function updateComposerState() {
  const message = document.querySelector("#message");
  const submit = document.querySelector("#capture-submit");
  document.querySelector("#message-count").textContent = message.value.length.toLocaleString("es-PY");
  submit.disabled = !message.value.trim() || submit.dataset.busy === "true";
  message.style.height = "auto";
  message.style.height = `${Math.min(message.scrollHeight, 144)}px`;
}

function appendUserMessage(message) {
  const log = document.querySelector("#capture-result");
  log.insertAdjacentHTML("beforeend", `
    <article class="chat-message user-message">
      <div class="user-bubble"><p>${escapeHtml(message)}</p><time>${messageTime()}</time></div>
    </article>`);
  scrollChatToEnd();
}

function appendPendingAssistantMessage() {
  const log = document.querySelector("#capture-result");
  const element = document.createElement("article");
  element.className = "chat-message assistant-message";
  element.innerHTML = `
    <span class="message-avatar" aria-hidden="true"><i data-lucide="sprout"></i></span>
    <div class="assistant-content">
      <div class="message-meta"><strong>Granja Luna</strong><span>${messageTime()}</span></div>
      ${renderProcessTrace([
        { title: "Entrada recibida", detail: "El mensaje ya está en el runtime.", state: "complete" },
        { title: "Analizando", detail: "Interpretando datos y aplicando reglas operativas.", state: "active" },
      ], true)}
    </div>`;
  log.appendChild(element);
  refreshIcons();
  scrollChatToEnd();
  return element;
}

function renderCaptureResult(entry, target = null) {
  const result = target || document.querySelector("#capture-result");
  const classification = entry.classification;
  const missing = entry.missing_data || [];
  const uiResponse = entry.dry_run?.ui_response;
  if (!target) {
    const wrapper = document.createElement("article");
    wrapper.className = "chat-message assistant-message";
    wrapper.innerHTML = '<span class="message-avatar" aria-hidden="true"><i data-lucide="sprout"></i></span><div class="assistant-content"></div>';
    result.appendChild(wrapper);
    target = wrapper;
  }
  target.dataset.chatEntry = entry.id;
  target.innerHTML = `
    <span class="message-avatar" aria-hidden="true"><i data-lucide="sprout"></i></span>
    <div class="assistant-content">
      <div class="message-meta"><strong>Granja Luna</strong><span>${messageTime()}</span></div>
      ${renderProcessTrace([
        { title: "Entrada recibida", detail: "El runtime recibió el relato.", state: "complete" },
        { title: "Interpretación preparada", detail: `${formatPlainToken(classification.intent)} · ${formatPlainToken(classification.primary_domain)}`, state: "complete" },
        { title: "Política evaluada", detail: `Riesgo ${classification.risk_level}; ${classification.requires_confirmation ? "requiere confirmación" : "no requiere confirmación"}.`, state: "complete" },
        { title: "Entrada guardada en el inbox", detail: `${reviewStatusLabels[entry.review_status] || entry.review_status || "Pendiente"} para revisión.`, state: "complete" },
      ])}
      ${["1.0", "1.1"].includes(uiResponse?.schema_version) ? renderUIResponse(uiResponse) : renderCaptureFallback(entry, classification, missing)}
    </div>`;
  bindUIActions(target, entry);
  refreshIcons();
  scrollChatToEnd();
}

function renderCaptureFallback(entry, classification, missing) {
  return `
    <div class="response-intro">
      <div class="response-title-row"><h2>Entrada guardada</h2><span class="risk-pill risk-${normalizedRisk(classification.risk_level)}">${escapeHtml(classification.risk_level)}</span></div>
      <p>Preparé una interpretación para que la revises antes de avanzar.</p>
    </div>
    <div class="result-grid">
      <div class="result-metric"><span>Intención</span><strong>${formatToken(classification.intent)}</strong></div>
      <div class="result-metric"><span>Dominio</span><strong>${formatToken(classification.primary_domain)}</strong></div>
      <div class="result-metric"><span>Confirmación</span><strong>${classification.requires_confirmation ? "Requerida" : "No requerida"}</strong></div>
      <div class="result-metric"><span>Estado</span><strong>${reviewStatusLabel(entry)}</strong></div>
    </div>
    ${renderDetectedData(entry, true)}
    ${missing.length ? `<div class="missing-block"><h3>Datos por completar o verificar</h3><ul>${missing.slice(0, 5).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}`;
}

function renderCaptureError(target, message) {
  target.innerHTML = `
    <span class="message-avatar" aria-hidden="true"><i data-lucide="triangle-alert"></i></span>
    <div class="assistant-content">
      <div class="message-meta"><strong>Granja Luna</strong><span>${messageTime()}</span></div>
      ${renderProcessTrace([
        { title: "Entrada recibida", detail: "El mensaje se preparó para enviar.", state: "complete" },
        { title: "No se pudo completar", detail: message, state: "error" },
      ])}
      <div class="assistant-error"><p>${escapeHtml(message)}. Dejé el texto en el compositor para que puedas reintentar.</p></div>
    </div>`;
  refreshIcons();
}

function renderProcessTrace(steps, open = false) {
  const complete = steps.every((step) => step.state === "complete");
  return `<details class="agent-process" ${open ? "open" : ""}>
    <summary><span class="process-summary-main">${complete ? '<i data-lucide="circle-check"></i>' : '<span class="process-pulse"></span>'}<span>${complete ? "Proceso completado" : "Procesando con Granja Luna"}</span></span><i data-lucide="chevron-down"></i></summary>
    <ol class="process-list">${steps.map((step) => `<li class="process-step is-${escapeHtml(step.state)}"><span class="process-state-icon">${step.state === "complete" ? '<i data-lucide="check"></i>' : step.state === "error" ? '<i data-lucide="x"></i>' : '<i class="spin" data-lucide="loader-circle"></i>'}</span><div><strong>${escapeHtml(step.title)}</strong><span>${escapeHtml(step.detail)}</span></div></li>`).join("")}</ol>
  </details>`;
}

function renderUIResponse(response) {
  const components = Array.isArray(response.components) ? response.components.map(renderUIComponent).filter(Boolean).join("") : "";
  return `
    <div class="response-intro">
      <div class="response-title-row"><h2>${escapeHtml(response.title || "Respuesta de Granja Luna")}</h2><span class="risk-pill risk-${normalizedRisk(response.risk_level)}">${escapeHtml(riskLabel(response.risk_level))}</span></div>
      ${response.summary ? `<p>${escapeHtml(response.summary)}</p>` : ""}
    </div>
    <div class="ui-stack">${components || renderNoticeComponent({ title: "Respuesta preparada", body: response.summary || "Revisá la información antes de continuar." })}</div>`;
}

function renderUIComponent(component) {
  if (!component || typeof component !== "object" || !component.props || typeof component.props !== "object") return "";
  const props = component.props;
  const renderers = {
    summary_card: renderSummaryComponent,
    data_table: renderDataTableComponent,
    checklist: renderChecklistComponent,
    field_group: renderFieldGroupComponent,
    action_group: renderActionGroupComponent,
    metric_grid: renderMetricGridComponent,
    chart: renderBarChartComponent,
    bar_chart: renderBarChartComponent,
    timeline: renderTimelineComponent,
    link_group: renderLinkGroupComponent,
    notice: renderNoticeComponent,
  };
  try {
    return renderers[component.component]?.(props) || "";
  } catch (_error) {
    return "";
  }
}

function uiCard(title, body, classes = "") {
  return `<section class="ui-card ${classes}">${title ? `<header class="ui-card-header"><h3>${escapeHtml(title)}</h3></header>` : ""}<div class="ui-card-body">${body}</div></section>`;
}

function renderSummaryComponent(props) {
  const body = props.body || props.summary || "";
  const data = props.data && typeof props.data === "object" && !Array.isArray(props.data) ? renderKeyValues(props.data) : "";
  return uiCard(props.title || "Resumen", `${body ? `<p>${escapeHtml(body)}</p>` : ""}${data}`);
}

function renderDataTableComponent(props) {
  const rows = Array.isArray(props.rows) ? props.rows.filter((row) => row && typeof row === "object").slice(0, 50) : [];
  if (!rows.length) return uiCard(props.title || "Datos", '<p>No hay filas para mostrar.</p>');
  const columns = [...new Set(rows.flatMap((row) => Object.keys(row)))].slice(0, 10);
  const detectedClass = String(props.title || "").toLocaleLowerCase("es").includes("items detectados") ? "detected-row" : "";
  const table = `<div class="ui-table-wrap"><table class="ui-table"><thead><tr>${columns.map((column) => `<th scope="col">${escapeHtml(formatPlainToken(column))}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr class="${detectedClass}">${columns.map((column) => `<td data-label="${escapeHtml(formatPlainToken(column))}">${escapeHtml(formatDisplayValue(row[column]))}</td>`).join("")}</tr>`).join("")}</tbody></table></div>${Array.isArray(props.rows) && props.rows.length > rows.length ? `<p>Se muestran ${rows.length} de ${props.rows.length} filas.</p>` : ""}`;
  return uiCard(props.title || "Datos", table);
}

function renderChecklistComponent(props) {
  const items = Array.isArray(props.items) ? props.items : [];
  const list = `<ul class="ui-checklist">${items.map((item) => {
    const label = typeof item === "object" && item ? item.label || item.title || item.text : item;
    const checked = typeof item === "object" && item && (item.checked === true || item.status === "complete" || item.status === "confirmed");
    return `<li><i data-lucide="${checked ? "circle-check" : "circle-dashed"}"></i><span>${escapeHtml(label)}</span></li>`;
  }).join("")}</ul>`;
  return uiCard(props.title || "Lista de revisión", list);
}

function renderFieldGroupComponent(props) {
  const values = props.values && typeof props.values === "object" ? props.values : {};
  const fields = Array.isArray(props.fields) ? Object.fromEntries(props.fields
    .filter((field) => field && typeof field === "object")
    .map((field) => [field.label || field.name || "Campo", field.value])) : values;
  return uiCard(props.title || "Datos", renderKeyValues(fields));
}

function renderActionGroupComponent(props) {
  const actions = Array.isArray(props.actions)
    ? props.actions.filter((action) => action && typeof action === "object").slice(0, 20)
    : [];
  if (!actions.length) return "";
  return `<section class="ui-card"><div class="ui-actions">${actions.map((action) => {
    const icon = action.id === "confirm" ? "check" : action.id === "edit" ? "pencil" : action.href ? "arrow-up-right" : "x";
    const safeHref = safeLink(action.app_url || action.url || action.href);
    return `<button class="ui-action" type="button" data-ui-action="${escapeHtml(action.id || "open")}" ${safeHref ? `data-ui-href="${escapeHtml(safeHref)}"` : ""}><i data-lucide="${icon}"></i><span>${escapeHtml(action.label || "Abrir")}</span></button>`;
  }).join("")}</div></section>`;
}

function renderMetricGridComponent(props) {
  let metrics = Array.isArray(props.metrics) ? props.metrics : Array.isArray(props.items) ? props.items : null;
  if (!metrics && props.values && typeof props.values === "object") metrics = Object.entries(props.values).map(([label, value]) => ({ label, value }));
  metrics = metrics || [];
  const body = `<div class="metric-grid">${metrics.map((metric, index) => {
    const item = metric && typeof metric === "object" ? metric : { label: `Dato ${index + 1}`, value: metric };
    return `<div class="metric-tile"><span>${escapeHtml(item.label || item.title || item.name || "Dato")}</span><strong>${escapeHtml(formatDisplayValue(item.value ?? item.amount ?? item.total ?? item.count))}</strong>${item.detail || item.trend ? `<small>${escapeHtml(item.detail || item.trend)}</small>` : ""}</div>`;
  }).join("")}</div>`;
  return uiCard(props.title || "Indicadores", body);
}

function renderBarChartComponent(props) {
  const values = Array.isArray(props.items) ? props.items : Array.isArray(props.data) ? props.data : Array.isArray(props.series) ? props.series : [];
  const points = values.map((item, index) => typeof item === "object" && item ? {
    label: item.label || item.name || item.category || `Dato ${index + 1}`,
    value: Number(item.value ?? item.amount ?? item.total ?? item.count ?? 0),
  } : { label: `Dato ${index + 1}`, value: Number(item) }).filter((item) => Number.isFinite(item.value));
  const configuredMax = Number(props.max);
  const max = Number.isFinite(configuredMax) && configuredMax > 0 ? configuredMax : Math.max(...points.map((item) => Math.abs(item.value)), 1);
  const body = `${props.description ? `<p>${escapeHtml(props.description)}</p>` : ""}${points.length ? `<div class="bar-chart" role="img" aria-label="${escapeHtml(props.title || "Gráfico de barras")}">${points.map((item) => `<div class="bar-row"><span class="bar-label" title="${escapeHtml(item.label)}">${escapeHtml(item.label)}</span><span class="bar-track"><span class="bar-fill" style="width:${Math.min(100, Math.max(2, Math.round(Math.abs(item.value) / max * 100)))}%"></span></span><strong class="bar-value">${escapeHtml(formatDisplayValue(item.value))}</strong></div>`).join("")}</div>` : '<p>No hay datos para graficar.</p>'}`;
  return uiCard(props.title || "Gráfico", body);
}

function renderTimelineComponent(props) {
  const items = Array.isArray(props.items) ? props.items : Array.isArray(props.events) ? props.events : [];
  const body = `<ol class="ui-timeline">${items.map((item) => {
    const event = item && typeof item === "object" ? item : { title: item };
    return `<li class="timeline-item"><span class="timeline-dot" aria-hidden="true"></span><div class="timeline-copy"><strong>${escapeHtml(event.title || event.label || event.event || "Evento")}</strong>${event.body || event.description || event.detail ? `<span>${escapeHtml(event.body || event.description || event.detail)}</span>` : ""}${event.date || event.time ? `<time>${escapeHtml(event.date || event.time)}</time>` : ""}</div></li>`;
  }).join("")}</ol>`;
  return uiCard(props.title || "Cronología", body);
}

function renderLinkGroupComponent(props) {
  const links = Array.isArray(props.links) ? props.links : Array.isArray(props.items) ? props.items : [];
  const safeLinks = links
    .filter((link) => link && typeof link === "object")
    .map((link) => {
      const target = link.target;
      if (target && typeof target === "object") {
        if (target.kind === "internal_route") {
          const route = internalView(target.value);
          return route ? { ...link, route } : null;
        }
        const safeHref = safeTypedLink(target.kind, target.value);
        return safeHref ? { ...link, safeHref } : null;
      }
      const safeHref = safeLink(link.app_url || link.url || link.href);
      return safeHref ? { ...link, safeHref } : null;
    })
    .filter(Boolean)
    .slice(0, 12);
  if (!safeLinks.length) return "";
  const body = `<div class="ui-links">${safeLinks.map((link) => {
    const copy = `<span><strong>${escapeHtml(link.label || link.title || "Abrir enlace")}</strong>${link.description ? `<small>${escapeHtml(link.description)}</small>` : ""}</span>`;
    if (link.route) return `<button class="ui-link" type="button" data-ui-route="${escapeHtml(link.route)}">${copy}<i data-lucide="arrow-right"></i></button>`;
    return `<a class="ui-link" href="${escapeHtml(link.safeHref)}" ${isExternalWebLink(link.safeHref) ? 'target="_blank" rel="noopener noreferrer"' : ""}>${copy}<i data-lucide="arrow-up-right"></i></a>`;
  }).join("")}</div>`;
  return uiCard(props.title || "Enlaces", body);
}

function renderNoticeComponent(props) {
  const tone = props.tone === "error" ? "danger" : ["warning", "danger", "success"].includes(props.tone) ? props.tone : "info";
  return uiCard(props.title || "Información", `<p>${escapeHtml(props.body || props.message || "")}</p>`, `ui-notice tone-${tone}`);
}

function renderKeyValues(values) {
  const entries = Object.entries(values || {}).slice(0, 12);
  if (!entries.length) return "";
  return `<div class="ui-kv-grid">${entries.map(([label, value]) => `<div class="ui-kv"><span>${escapeHtml(formatPlainToken(label))}</span><strong>${escapeHtml(formatDisplayValue(value))}</strong></div>`).join("")}</div>`;
}

function bindUIActions(container, entry) {
  container.querySelectorAll("[data-ui-route]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.uiRoute));
  });
  container.querySelectorAll("[data-ui-action]").forEach((button) => {
    button.addEventListener("click", async () => {
      const href = safeLink(button.dataset.uiHref);
      if (href) {
        if (isExternalWebLink(href)) window.open(href, "_blank", "noopener,noreferrer");
        else window.location.href = href;
        return;
      }
      await switchView("inbox");
      await openEntry(entry.id);
      if (button.dataset.uiAction === "confirm") showToast("Revisá los datos y confirmá explícitamente en la ficha");
    });
  });
}

function internalView(value) {
  const normalized = String(value || "").toLowerCase().replaceAll("-", "_");
  return {
    chat: "capture",
    capture: "capture",
    captura: "capture",
    inbox: "inbox",
    bandeja: "inbox",
    activity: "activity",
    actividad: "activity",
    operations: "operations",
    operaciones: "operations",
    cria: "operations",
    incubacion: "operations",
  }[normalized] || "";
}

function safeTypedLink(kind, value) {
  const safe = safeLink(value);
  if (!safe) return null;
  if (kind === "external_url") return isExternalWebLink(safe) ? safe : null;
  if (kind === "domain_app") return /^(?:personal-agent|granja-luna):/i.test(safe) ? safe : null;
  return null;
}

function safeLink(value) {
  if (!value || typeof value !== "string") return null;
  const trimmed = value.trim();
  if (trimmed.startsWith("#") || (trimmed.startsWith("/") && !trimmed.startsWith("//"))) {
    return trimmed;
  }
  try {
    const parsed = new URL(trimmed);
    if (parsed.username || parsed.password) return null;
    return ["http:", "https:", "personal-agent:", "granja-luna:"].includes(parsed.protocol) ? trimmed : null;
  } catch (_error) {
    return null;
  }
}

function isExternalWebLink(value) {
  return /^https?:/i.test(value || "");
}

function normalizedRisk(value) {
  const risks = { bajo: "low", medio: "medium", alto: "high", critico: "critical" };
  return risks[value] || ["low", "medium", "high", "critical"].includes(value) ? (risks[value] || value) : "medium";
}

function riskLabel(value) {
  return { low: "Bajo", medium: "Medio", high: "Alto", critical: "Crítico", bajo: "Bajo", medio: "Medio", alto: "Alto", critico: "Crítico" }[value] || value || "Medio";
}

function formatDisplayValue(value) {
  if (value == null || value === "") return "—";
  if (typeof value === "boolean") return value ? "Sí" : "No";
  if (Array.isArray(value)) {
    if (value.some((item) => item && typeof item === "object")) return `${value.length} registro${value.length === 1 ? "" : "s"}`;
    return value.join(", ");
  }
  if (typeof value === "object") {
    const summary = Object.entries(value).slice(0, 4).map(([key, item]) => `${formatPlainToken(key)}: ${formatDisplayValue(item)}`).join(" · ");
    return summary || "—";
  }
  return typeof value === "number" ? new Intl.NumberFormat("es-PY").format(value) : String(value);
}

function messageTime() {
  return new Intl.DateTimeFormat("es-PY", { hour: "2-digit", minute: "2-digit" }).format(new Date());
}

function scrollChatToEnd() {
  requestAnimationFrame(() => window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" }));
}

function bindVoiceInput() {
  document.querySelector("#voice-button").addEventListener("click", () => {
    if (state.voice.active) stopVoiceInput();
    else startVoiceInput();
  });
  window.addEventListener("agent:native-voice", (event) => handleNativeVoiceEvent(event.detail));
  window.addEventListener("message", (event) => handleNativeVoiceEvent(event.data));
  document.addEventListener("message", (event) => handleNativeVoiceEvent(event.data));
}

function startVoiceInput() {
  const message = document.querySelector("#message");
  state.voice.baseText = message.value.trimEnd();
  state.voice.requestId = `voice-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  if (window.ReactNativeWebView?.postMessage) {
    window.ReactNativeWebView.postMessage(JSON.stringify({
      protocol: "agent.voice.v1",
      type: "speech.start",
      requestId: state.voice.requestId,
      lang: "es-PY",
    }));
    setVoiceStatus(true, "Preparando el micrófono…");
    return;
  }
  startBrowserSpeechRecognition();
}

function stopVoiceInput() {
  if (window.ReactNativeWebView?.postMessage && state.voice.requestId) {
    window.ReactNativeWebView.postMessage(JSON.stringify({ protocol: "agent.voice.v1", type: "speech.stop", requestId: state.voice.requestId, lang: "es-PY" }));
  }
  state.voice.recognition?.stop();
  setVoiceStatus(true, "Finalizando dictado…");
}

function cancelVoiceInput() {
  const requestId = state.voice.requestId;
  if (window.ReactNativeWebView?.postMessage && requestId) {
    window.ReactNativeWebView.postMessage(JSON.stringify({
      protocol: "agent.voice.v1",
      type: "speech.stop",
      requestId,
      lang: "es-PY",
    }));
  }
  if (state.voice.recognition) {
    state.voice.recognition.onresult = null;
    state.voice.recognition.onerror = null;
    state.voice.recognition.onend = null;
    state.voice.recognition.abort();
  }
  state.voice.recognition = null;
  state.voice.requestId = null;
  state.voice.baseText = "";
  setVoiceStatus(false, "");
  document.querySelector("#voice-status").hidden = true;
}

function startBrowserSpeechRecognition() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    finishVoiceInput("El dictado no está disponible en este navegador", true);
    showToast("Este navegador no ofrece reconocimiento de voz");
    return;
  }
  const recognition = new Recognition();
  const requestId = state.voice.requestId;
  state.voice.recognition = recognition;
  recognition.lang = "es-PY";
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.onstart = () => setVoiceStatus(true, "Escuchando…");
  recognition.onresult = (event) => {
    if (!requestId || state.voice.requestId !== requestId) return;
    let transcript = "";
    for (let index = 0; index < event.results.length; index += 1) transcript += event.results[index][0]?.transcript || "";
    applyVoiceTranscript(transcript);
  };
  recognition.onerror = (event) => {
    if (state.voice.requestId === requestId) finishVoiceInput(voiceErrorLabel(event.error), true);
  };
  recognition.onend = () => {
    if (state.voice.requestId !== requestId) return;
    state.voice.recognition = null;
    if (state.voice.active) finishVoiceInput("Dictado listo para editar");
  };
  try {
    recognition.start();
    setVoiceStatus(true, "Preparando el micrófono…");
  } catch (error) {
    finishVoiceInput(error.message || "No se pudo iniciar el micrófono", true);
  }
}

function handleNativeVoiceEvent(payload) {
  if (typeof payload === "string") {
    try { payload = JSON.parse(payload); } catch (_error) { return; }
  }
  if (!payload || payload.protocol !== "agent.voice.v1") return;
  if (!state.voice.requestId || payload.requestId !== state.voice.requestId) return;
  if (payload.type === "speech.result") {
    applyVoiceTranscript(payload.transcript || "");
    if (payload.isFinal || payload.is_final) setVoiceStatus(true, "Finalizando dictado…");
    return;
  }
  if (payload.type === "speech.error") {
    finishVoiceInput(voiceErrorLabel(payload.error), true);
    return;
  }
  if (payload.type === "speech.state") {
    const labels = {
      "requesting-permission": "Solicitando permiso…",
      requesting_permission: "Solicitando permiso…",
      starting: "Preparando el micrófono…",
      ready: "Micrófono listo",
      listening: "Escuchando…",
      processing: "Transcribiendo…",
      stopping: "Deteniendo el dictado…",
    };
    if (["end", "ended", "idle", "stopped"].includes(payload.state)) finishVoiceInput("Dictado listo para editar");
    else setVoiceStatus(true, labels[payload.state] || "Escuchando…");
  }
}

function applyVoiceTranscript(transcript) {
  const message = document.querySelector("#message");
  const separator = state.voice.baseText && transcript.trim() ? " " : "";
  message.value = `${state.voice.baseText}${separator}${transcript.trimStart()}`;
  updateComposerState();
}

function setVoiceStatus(active, label, isError = false) {
  state.voice.active = active;
  const button = document.querySelector("#voice-button");
  const status = document.querySelector("#voice-status");
  clearTimeout(state.voice.statusTimer);
  button.setAttribute("aria-pressed", String(active));
  button.setAttribute("aria-label", active ? "Detener dictado" : "Iniciar dictado");
  button.disabled = active && label === "Finalizando dictado…";
  status.hidden = false;
  status.classList.toggle("is-error", isError);
  document.querySelector("#voice-status-label").textContent = label;
  refreshIcons();
}

function finishVoiceInput(label, isError = false) {
  setVoiceStatus(false, label, isError);
  state.voice.recognition = null;
  state.voice.requestId = null;
  state.voice.baseText = document.querySelector("#message").value;
  state.voice.statusTimer = setTimeout(() => { document.querySelector("#voice-status").hidden = true; }, isError ? 4200 : 2200);
  document.querySelector("#message").focus();
}

function voiceErrorLabel(error) {
  const labels = { "not-allowed": "Permiso de micrófono denegado", "audio-capture": "No se encontró un micrófono", "no-speech": "No detecté voz", network: "Error de red al transcribir" };
  return labels[error] || String(error || "No se pudo transcribir el audio");
}

function bindInboxControls() {
  document.querySelector("#refresh-inbox").addEventListener("click", loadInbox);
  document.querySelectorAll("#inbox-filters button").forEach((button) => {
    button.addEventListener("click", async () => {
      state.inboxFilter = button.dataset.status;
      document.querySelectorAll("#inbox-filters button").forEach((item) => item.classList.toggle("is-selected", item === button));
      await loadInbox();
    });
  });
}

async function loadInbox() {
  const list = document.querySelector("#inbox-list");
  list.innerHTML = loadingMarkup("Cargando inbox");
  refreshIcons();
  try {
    const query = state.inboxFilter === "all" ? "" : `?status=${encodeURIComponent(state.inboxFilter)}`;
    renderInbox(await api(`/api/inbox${query}`));
  } catch (error) {
    list.innerHTML = errorMarkup(error.message);
    refreshIcons();
  }
}

function renderInbox(entries) {
  const list = document.querySelector("#inbox-list");
  if (!entries.length) {
    list.innerHTML = emptyMarkup("inbox", "No hay entradas con este estado");
    refreshIcons();
    return;
  }
  list.innerHTML = entries.map((entry) => {
    const classification = entry.classification;
    return `
      <button class="entry-card" type="button" data-entry-id="${escapeHtml(entry.id)}">
        <div class="entry-card-top">
          <span class="status-badge status-${escapeHtml(entry.review_status)}">${reviewStatusLabel(entry)}</span>
          <span class="risk-badge risk-${escapeHtml(classification.risk_level)}">${escapeHtml(classification.risk_level)}</span>
        </div>
        <h3>${escapeHtml(entry.message)}</h3>
        <div class="entry-card-bottom">
          <span class="entry-meta"><i data-lucide="folder"></i><span>${formatToken(classification.primary_domain)}</span></span>
          <time>${formatDate(entry.created_at)}</time>
        </div>
      </button>`;
  }).join("");
  list.querySelectorAll(".entry-card").forEach((button) => button.addEventListener("click", () => openEntry(button.dataset.entryId)));
  refreshIcons();
}

async function refreshInboxSummary() {
  try {
    const summary = await api("/api/inbox/summary");
    const statuses = summary.by_review_status || {};
    const pending = (statuses.pending || 0) + (statuses.needs_information || 0) + (statuses.needs_correction || 0);
    document.querySelector("#pending-count").textContent = pending;
    const badge = document.querySelector("#nav-inbox-badge");
    badge.hidden = pending === 0;
    badge.textContent = pending > 99 ? "99+" : String(pending);
  } catch (_error) {
    // Connection status already communicates availability.
  }
}

async function openEntry(entryId) {
  try {
    const [entry, reviewEvents] = await Promise.all([
      api(`/api/inbox/${encodeURIComponent(entryId)}`),
      api(`/api/review-events?entry_id=${encodeURIComponent(entryId)}`),
    ]);
    state.selectedEntry = entry;
    state.reviewEvents = reviewEvents;
    state.editingSection = null;
    renderEntrySheet();
    document.querySelector("#sheet-backdrop").hidden = false;
    document.querySelector("#entry-sheet").hidden = false;
    document.body.style.overflow = "hidden";
    refreshIcons();
  } catch (error) {
    showToast(error.message);
  }
}

function renderEntrySheet() {
  const entry = state.selectedEntry;
  const classification = entry.classification;
  const content = document.querySelector("#sheet-content");
  content.innerHTML = `
    <section class="source-section">
      <p class="eyebrow">Entrada original</p>
      <p class="sheet-message">${escapeHtml(entry.message)}</p>
      <time>${formatDate(entry.created_at, true)}</time>
    </section>
    <section class="review-section interpretation-section">
      ${sectionHeading("Interpretación", "classification", "Corregir clasificación")}
      <div class="sheet-meta-grid">
        ${interpretationCard("Estado", reviewStatusLabel(entry), `status-card status-${entry.review_status}`)}
        ${interpretationCard("Riesgo", classification.risk_level, `risk-card risk-${classification.risk_level}`, entry.classification_provenance?.risk_level)}
        ${interpretationCard("Intención", formatPlainToken(classification.intent), "neutral-card", entry.classification_provenance?.intent)}
        ${interpretationCard("Dominio", formatPlainToken(classification.primary_domain), "neutral-card", entry.classification_provenance?.primary_domain)}
      </div>
    </section>
    ${renderEntryData(entry)}
    ${renderReviewHistory()}
    ${renderReviewActions(entry)}
  `;
  bindEntrySheetEvents();
  refreshIcons();
}

function interpretationCard(label, value, classes, provenance = null) {
  return `<div class="sheet-meta-item ${classes}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>${provenance ? provenanceBadge(provenance) : ""}</div>`;
}

function sectionHeading(title, section, tooltip) {
  return `
    <div class="section-heading-row">
      <h3>${escapeHtml(title)}</h3>
      <button class="section-edit-button" type="button" data-edit-section="${section}" title="${escapeHtml(tooltip)}">
        <i data-lucide="pencil"></i><span class="sr-only">${escapeHtml(tooltip)}</span>
      </button>
    </div>`;
}

function renderEntryData(entry) {
  if (entry.structured_data?.schema_id === "purchase.v2") return renderPurchaseReview(entry);
  return renderDetectedData(entry);
}

function renderPurchaseReview(entry) {
  const structured = entry.structured_data;
  const values = structured.values || {};
  const provenance = structured.provenance || { fields: {}, items: [] };
  return `
    <section class="review-section purchase-review" data-schema-id="purchase.v2">
      <div class="review-section-title"><p class="eyebrow">Compra detectada</p><span class="schema-badge">purchase.v2</span></div>
      <section class="purchase-subsection">
        ${sectionHeading("Datos generales", "purchase_general", "Editar datos generales")}
        ${renderPurchaseGeneralReadOnly(values, provenance.fields || {})}
      </section>
      <section class="purchase-subsection">
        ${sectionHeading("Productos comprados", "purchase_items", "Editar productos")}
        ${renderPurchaseItemsReadOnly(values, provenance.items || [])}
      </section>
    </section>
  `;
}

function renderPurchaseGeneralReadOnly(values, provenance) {
  return `<div class="data-value-grid">
    ${dataValue("Fecha de compra", values.fecha_compra ? formatDateOnly(values.fecha_compra) : null, "fecha_compra", provenance.fecha_compra, true)}
    ${dataValue("Proveedor", values.proveedor, "proveedor", provenance.proveedor, true)}
    ${dataValue("Moneda", values.moneda, "moneda", provenance.moneda, true)}
    ${dataValue("Comprobante", values.comprobante, "comprobante", provenance.comprobante, false)}
    ${values.descuento ? dataValue("Descuento", formatDiscount(values.descuento), "descuento", provenance.descuento, false) : ""}
    ${values.total_declarado != null ? dataValue("Total declarado", formatMoney(values.total_declarado), "total_declarado", provenance.total_declarado, false) : ""}
  </div>`;
}

function dataValue(label, value, path, provenance, required) {
  const missing = value == null || value === "";
  return `
    <div class="data-value ${missing ? (required ? "is-missing" : "is-empty-optional") : ""}" data-field-path="${path}">
      <div class="data-value-label"><span>${escapeHtml(label)}</span>${missing && !required ? "" : provenanceBadge(provenance || (missing ? "missing" : "extracted"))}</div>
      <strong>${escapeHtml(missing ? (required ? "Dato obligatorio pendiente" : "-") : value)}</strong>
      ${missing && required ? '<span class="required-field-alert"><i data-lucide="triangle-alert"></i>Requiere revisión</span>' : ""}
    </div>`;
}

function renderPurchaseItemsReadOnly(values, provenanceItems) {
  const items = values.items || [];
  if (!items.length) return `<div class="empty-inline" data-field-path="items">No se detectaron productos.</div>`;
  const totals = calculatePurchaseTotals(items, values.descuento);
  const hasMismatch = values.total_declarado != null && totals.total != null && Number(values.total_declarado) !== totals.total;
  return `
    <div class="purchase-read-items">
      ${items.map((item, index) => {
        const provenance = provenanceItems[index] || {};
        const itemProvenance = ["corrected", "enriched", "clarified"].find((value) => Object.values(provenance).includes(value)) || provenance.producto || "extracted";
        return `
          <article class="purchase-read-item" data-field-path="items.${index}">
            <div class="purchase-read-main">
              <div><strong>${escapeHtml(item.producto || "Producto pendiente")}</strong>${provenanceBadge(itemProvenance)}</div>
              <span>${escapeHtml(formatQuantity(item.cantidad, item.unidad))}</span>
            </div>
            <div class="purchase-read-price">
              <strong>${formatMoney(item.precio_unitario)}</strong>
              <span>${item.subtotal_inferido == null ? "Sin subtotal" : `Subtotal ${formatMoney(item.subtotal_inferido)}`}</span>
            </div>
          </article>`;
      }).join("")}
    </div>
    <div class="purchase-totals">
      <div><span>Subtotal</span><strong>${formatMoney(totals.subtotal)}</strong></div>
      ${values.descuento ? `<div><span>Descuento</span><strong>- ${formatMoney(totals.discountAmount)}</strong></div>` : ""}
      <div class="purchase-total-final"><span>Total calculado</span><strong>${formatMoney(totals.total)}</strong></div>
    </div>
    ${hasMismatch ? `<div class="total-mismatch"><i data-lucide="triangle-alert"></i><span>El total declarado (${formatMoney(values.total_declarado)}) no coincide con el total calculado.</span></div>` : ""}
  `;
}

function provenanceBadge(provenance) {
  const label = provenanceLabels[provenance] || formatPlainToken(provenance || "");
  return `<small class="provenance-badge provenance-${escapeHtml(provenance || "missing")}">${escapeHtml(label)}</small>`;
}

function renderPurchaseGeneralEditor(values) {
  const discount = values.descuento;
  return `
    <form class="section-editor" id="correction-form" data-section="purchase_general">
      <div class="field-grid">
        ${purchaseField("fecha_compra", "Fecha de compra", "date", values.fecha_compra, true)}
        ${purchaseField("proveedor", "Proveedor", "text", values.proveedor, true, "Nombre o referencia")}
        <label class="field" data-field-path="moneda"><span>Moneda <em>Obligatorio</em></span><select id="purchase-moneda"><option value="PYG">Guaranies (PYG)</option></select></label>
        ${purchaseField("comprobante", "Comprobante o referencia", "text", values.comprobante, false, "Opcional")}
        ${values.total_declarado != null ? purchaseField("total_declarado", "Total declarado", "number", values.total_declarado, false) : ""}
      </div>
      <div class="optional-adjustment">
        <button class="secondary-icon-button" id="add-discount" type="button" ${discount ? "hidden" : ""}><i data-lucide="badge-percent"></i><span>Agregar descuento</span></button>
        <div class="discount-editor" id="discount-editor" ${discount ? "" : "hidden"}>
          <div class="field-grid">
            ${selectField("purchase-discount-type", "Tipo de descuento", ["monto", "porcentaje"], discount?.tipo || "monto")}
            ${purchaseField("discount-value", "Valor del descuento", "number", discount?.valor, false)}
          </div>
          <button class="text-danger-button" id="remove-discount" type="button"><i data-lucide="trash-2"></i><span>Quitar descuento</span></button>
        </div>
      </div>
      ${correctionFooter()}
    </form>`;
}

function renderPurchaseItemsEditor(items) {
  return `
    <form class="section-editor" id="correction-form" data-section="purchase_items">
      <div class="items-heading"><span></span><button class="secondary-icon-button" id="add-purchase-item" type="button"><i data-lucide="plus"></i><span>Agregar</span></button></div>
      <div class="purchase-items" id="purchase-items">${items.map((item, index) => purchaseItemMarkup(item, index, items.length)).join("")}</div>
      <div class="form-total"><span>Total calculado</span><strong id="purchase-total">${formatMoney(calculateItemsTotal(items))}</strong></div>
      ${correctionFooter()}
    </form>`;
}

function renderClassificationEditor(entry) {
  const classification = entry.classification;
  return `
    <form class="section-editor" id="correction-form" data-section="classification">
      <div class="field-grid">
        ${selectField("classification-intent", "Intención", intentOptions, classification.intent)}
        ${selectField("classification-domain", "Dominio principal", domainOptions, classification.primary_domain)}
        ${selectField("classification-risk", "Riesgo", ["bajo", "medio", "alto", "critico"], classification.risk_level, true)}
      </div>
      ${correctionFooter()}
    </form>`;
}

function selectField(id, label, options, selected, wide = false) {
  return `<label class="field ${wide ? "field-wide" : ""}"><span>${escapeHtml(label)}</span><select id="${id}">${options.map((option) => `<option value="${escapeHtml(option)}" ${option === selected ? "selected" : ""}>${formatToken(option)}</option>`).join("")}</select></label>`;
}

function correctionFooter() {
  return `
    <div class="correction-context">
      <label class="field"><span>Motivo de la modificación</span><select id="correction-reason" required>
        <option value="system_error">Corregir dato detectado</option>
        <option value="new_information">Agregar dato no mencionado</option>
        <option value="ambiguous_input">Resolver ambigüedad o contradicción</option>
      </select><small class="field-help" id="correction-reason-help">${escapeHtml(correctionReasonHelp.system_error)}</small></label>
      <label class="field"><span>Nota <em>Opcional</em></span><textarea id="correction-note" maxlength="2000" placeholder="Contexto útil sobre la corrección"></textarea></label>
    </div>
    <div class="editor-actions">
      <button class="secondary-button" type="button" id="cancel-correction">Cancelar</button>
      <button class="primary-button" type="submit"><i data-lucide="save"></i><span>Guardar corrección</span></button>
    </div>`;
}

function renderReviewHistory() {
  const superseded = new Set(state.reviewEvents.map((event) => event.supersedes_curation_event_id).filter(Boolean));
  const events = state.reviewEvents.filter((event) => !superseded.has(event.id));
  if (!events.length) return "";
  return `
    <details class="review-history">
      <summary><span><i data-lucide="history"></i>Historial de revisión</span><strong>${events.length}</strong></summary>
      <div class="review-history-list">
        ${events.map((event) => {
          const isCuration = ["feedback_curated", "feedback_curation_revised"].includes(event.event_type);
          const title = event.event_type === "feedback_curation_revised" ? "Curaduría corregida" : isCuration ? "Feedback curado" : event.event_type === "correction_saved" ? "Corrección guardada" : "Decisión de revisión";
          const reasonValue = isCuration ? event.curation?.primary_reason : event.reason;
          const reason = correctionReasonLabels[reasonValue] || formatPlainToken(reasonValue || "");
          const section = isCuration ? "curation" : event.section;
          const note = isCuration ? event.curation?.explanation : event.note;
          return `<article class="review-history-event">
            <div class="review-history-event-head"><div><strong>${title}</strong><span>${escapeHtml(reviewSectionLabels[section] || formatPlainToken(section))}</span></div><time>${formatDate(event.occurred_at, true)}</time></div>
            <span class="history-reason">${escapeHtml(reason)}</span>
            ${note ? `<p>${escapeHtml(note)}</p>` : ""}
            ${isCuration ? `<small>Uso: ${escapeHtml(trainingEligibilityLabels[event.curation?.training_eligibility] || formatPlainToken(event.curation?.training_eligibility))}</small>` : ""}
            ${event.changes?.length ? `<small>${event.changes.length} cambio${event.changes.length === 1 ? "" : "s"} registrado${event.changes.length === 1 ? "" : "s"}</small>` : ""}
          </article>`;
        }).join("")}
      </div>
    </details>`;
}

function renderReviewActions(entry) {
  if (entry.review_status !== "pending") {
    const messages = {
      validated: "Esta interpretación ya fue validada.",
      needs_information: "La revisión está esperando información adicional.",
      needs_correction: "La corrección quedó postergada.",
      rejected: "Esta entrada fue descartada.",
    };
    if (entry.review_status === "rejected") {
      return `<div class="review-state-summary"><i data-lucide="info"></i><span>${escapeHtml(messages.rejected)}</span></div>`;
    }
    return `<section class="review-actions"><div class="review-state-summary"><i data-lucide="info"></i><span>${escapeHtml(messages[entry.review_status] || "Revisión completada.")}</span></div><button class="danger-button discard-entry-button" id="discard-entry" type="button"><i data-lucide="archive-x"></i><span>Descartar entrada</span></button><form class="review-decision-panel" id="review-decision-panel" hidden></form></section>`;
  }
  return `
    <section class="review-actions">
      <div class="review-actions-main">
        <button class="primary-button" type="button" id="confirm-review"><i data-lucide="check"></i><span>Confirmar datos</span></button>
        <button class="secondary-button" type="button" id="needs-information"><i data-lucide="circle-help"></i><span>Falta información</span></button>
        <button class="icon-button" type="button" id="more-review-actions" title="Más acciones"><i data-lucide="ellipsis"></i><span class="sr-only">Más acciones</span></button>
      </div>
      <div class="review-more-menu" id="review-more-menu" hidden>
        <button type="button" data-review-mode="needs_correction"><i data-lucide="clock-3"></i><span>Corregir después</span></button>
        <button type="button" data-review-mode="system_issue"><i data-lucide="message-square-warning"></i><span>Reportar problema del sistema</span></button>
        <button type="button" data-review-mode="reject"><i data-lucide="archive-x"></i><span>Descartar entrada</span></button>
      </div>
      <form class="review-decision-panel" id="review-decision-panel" hidden></form>
    </section>`;
}

function bindEntrySheetEvents() {
  document.querySelectorAll("[data-edit-section]").forEach((button) => {
    button.addEventListener("click", () => openCorrectionModal(button.dataset.editSection));
  });
  document.querySelector("#confirm-review")?.addEventListener("click", () => submitReviewDecision("confirm"));
  document.querySelector("#needs-information")?.addEventListener("click", () => openReviewDecisionPanel("needs_information"));
  document.querySelector("#more-review-actions")?.addEventListener("click", () => {
    const menu = document.querySelector("#review-more-menu");
    menu.hidden = !menu.hidden;
  });
  document.querySelectorAll("[data-review-mode]").forEach((button) => button.addEventListener("click", () => openReviewDecisionPanel(button.dataset.reviewMode)));
  document.querySelector("#discard-entry")?.addEventListener("click", () => openReviewDecisionPanel("reject"));
}

function openCorrectionModal(section) {
  const entry = state.selectedEntry;
  const values = entry.structured_data?.values || {};
  const titles = {
    classification: "Corregir interpretación",
    purchase_general: "Editar datos generales",
    purchase_items: "Editar productos comprados",
  };
  state.editingSection = section;
  hideToast();
  document.querySelector("#correction-modal-title").textContent = titles[section];
  const content = document.querySelector("#correction-modal-content");
  if (section === "classification") content.innerHTML = renderClassificationEditor(entry);
  if (section === "purchase_general") content.innerHTML = renderPurchaseGeneralEditor(values);
  if (section === "purchase_items") content.innerHTML = renderPurchaseItemsEditor(values.items || []);
  document.querySelector("#correction-backdrop").hidden = false;
  document.querySelector("#correction-modal").hidden = false;
  bindCorrectionModalEvents();
  refreshIcons();
  content.querySelector("input, select, textarea")?.focus();
}

function bindCorrectionModalEvents() {
  const form = document.querySelector("#correction-form");
  if (form) {
    form.addEventListener("submit", saveCorrection);
    document.querySelector("#cancel-correction").addEventListener("click", closeCorrectionModal);
    if (state.editingSection === "purchase_items") {
      document.querySelector("#add-purchase-item").addEventListener("click", addPurchaseItem);
      bindPurchaseItemEvents();
    }
    if (state.editingSection === "purchase_general") {
      document.querySelector("#add-discount")?.addEventListener("click", () => setDiscountEditorVisible(true));
      document.querySelector("#remove-discount")?.addEventListener("click", () => setDiscountEditorVisible(false));
    }
    const reason = document.querySelector("#correction-reason");
    reason?.addEventListener("change", () => {
      document.querySelector("#correction-reason-help").textContent = correctionReasonHelp[reason.value];
    });
  }
}

function setDiscountEditorVisible(visible) {
  document.querySelector("#discount-editor").hidden = !visible;
  document.querySelector("#add-discount").hidden = visible;
  if (!visible) document.querySelector("#purchase-discount-value").value = "";
  refreshIcons();
}

async function saveCorrection(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const submit = form.querySelector('button[type="submit"]');
  submit.disabled = true;
  try {
    const section = form.dataset.section;
    const updated = await api(`/api/inbox/${encodeURIComponent(state.selectedEntry.id)}/correction`, {
      method: "PATCH",
      body: JSON.stringify({
        section,
        reason: document.querySelector("#correction-reason").value,
        note: document.querySelector("#correction-note").value || null,
        data: collectCorrectionData(section),
      }),
    });
    state.selectedEntry = updated;
    closeCorrectionModal();
    state.reviewEvents = await api(`/api/review-events?entry_id=${encodeURIComponent(updated.id)}`);
    renderEntrySheet();
    showToast("Corrección guardada");
    await Promise.all([loadInbox(), refreshInboxSummary()]);
  } catch (error) {
    showToast(error.message);
  } finally {
    submit.disabled = false;
    refreshIcons();
  }
}

function collectCorrectionData(section) {
  if (section === "classification") {
    return {
      intent: document.querySelector("#classification-intent").value,
      primary_domain: document.querySelector("#classification-domain").value,
      risk_level: document.querySelector("#classification-risk").value,
    };
  }
  if (section === "purchase_general") {
    const discountVisible = !document.querySelector("#discount-editor")?.hidden;
    return {
      fecha_compra: document.querySelector("#purchase-fecha_compra").value || null,
      proveedor: document.querySelector("#purchase-proveedor").value || null,
      moneda: document.querySelector("#purchase-moneda").value || "PYG",
      comprobante: document.querySelector("#purchase-comprobante").value || null,
      descuento: discountVisible ? {
        tipo: document.querySelector("#purchase-discount-type").value,
        valor: document.querySelector("#purchase-discount-value").value || null,
      } : null,
      total_declarado: document.querySelector("#purchase-total_declarado")?.value || null,
    };
  }
  return {
    items: [...document.querySelectorAll(".purchase-item")].map((item) => ({
      producto: item.querySelector('[data-item-field="producto"]').value,
      cantidad: item.querySelector('[data-item-field="cantidad"]').value || null,
      unidad: item.querySelector('[data-item-field="unidad"]').value,
      precio_unitario: item.querySelector('[data-item-field="precio_unitario"]').value || null,
    })),
  };
}

function openReviewDecisionPanel(mode) {
  const menu = document.querySelector("#review-more-menu");
  if (menu) menu.hidden = true;
  const panel = document.querySelector("#review-decision-panel");
  const config = {
    needs_information: { title: "Dejar pendiente por información", note: "Dato o contexto que falta", required: false, button: "Dejar pendiente" },
    needs_correction: { title: "Corregir después", note: "Qué debe corregirse", required: true, button: "Marcar para corregir" },
    system_issue: { title: "Reportar problema del sistema", note: "Describe la limitación o mejora necesaria", required: true, button: "Registrar problema" },
    reject: { title: "Descartar entrada", note: "Motivo adicional", required: false, button: "Descartar" },
  }[mode];
  panel.hidden = false;
  panel.dataset.mode = mode;
  panel.innerHTML = `
    <div><h3>${config.title}</h3><button class="section-edit-button" type="button" id="close-decision-panel" title="Cerrar"><i data-lucide="x"></i></button></div>
    ${mode === "reject" ? `<label class="field"><span>Motivo</span><select id="review-reason"><option value="not_relevant">No corresponde</option><option value="duplicate">Entrada duplicada</option><option value="test_entry">Entrada de prueba</option></select></label>` : ""}
    <label class="field"><span>${config.note}${config.required ? "" : " <em>Opcional</em>"}</span><textarea id="review-note" maxlength="2000" ${config.required ? "required" : ""}></textarea></label>
    <button class="${mode === "reject" ? "danger-button" : "primary-button"}" type="submit">${config.button}</button>`;
  panel.onsubmit = async (event) => {
    event.preventDefault();
    const decision = mode === "system_issue" ? "needs_correction" : mode;
    const reason = mode === "system_issue" ? "system_limitation" : document.querySelector("#review-reason")?.value || null;
    await submitReviewDecision(decision, reason, document.querySelector("#review-note").value || null);
  };
  panel.querySelector("#close-decision-panel").addEventListener("click", () => { panel.hidden = true; });
  refreshIcons();
}

async function submitReviewDecision(decision, reason = null, note = null) {
  try {
    await api(`/api/inbox/${encodeURIComponent(state.selectedEntry.id)}/review`, {
      method: "PATCH",
      body: JSON.stringify({ decision, reason, note }),
    });
    closeSheet();
    await Promise.all([loadInbox(), refreshInboxSummary()]);
    showToast(decision === "confirm" ? "Entrada validada" : "Revisión actualizada");
  } catch (error) {
    markReviewMissingFields(error.detail?.missing_fields || []);
    showToast(error.message);
  }
}

function markReviewMissingFields(fields) {
  document.querySelectorAll(".data-value.is-invalid, .purchase-read-item.is-invalid, .empty-inline.is-invalid").forEach((field) => field.classList.remove("is-invalid"));
  fields.forEach((missing) => {
    let target = document.querySelector(`[data-field-path="${CSS.escape(missing.path)}"]`);
    if (!target && missing.path.startsWith("items.")) target = document.querySelector(`[data-field-path="${CSS.escape(missing.path.split(".").slice(0, 2).join("."))}"]`);
    target?.classList.add("is-invalid");
  });
}

function bindSheetControls() {
  document.querySelector("#close-sheet").addEventListener("click", closeSheet);
  document.querySelector("#sheet-backdrop").addEventListener("click", closeSheet);
  document.querySelector("#close-correction-modal").addEventListener("click", closeCorrectionModal);
  document.querySelector("#correction-backdrop").addEventListener("click", closeCorrectionModal);
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (!document.querySelector("#correction-modal").hidden) {
      closeCorrectionModal();
    } else if (!document.querySelector("#entry-sheet").hidden) {
      closeSheet();
    }
  });
}

function closeCorrectionModal() {
  document.querySelector("#correction-backdrop").hidden = true;
  document.querySelector("#correction-modal").hidden = true;
  document.querySelector("#correction-modal-content").innerHTML = "";
  state.editingSection = null;
}

function closeSheet() {
  closeCorrectionModal();
  document.querySelector("#sheet-backdrop").hidden = true;
  document.querySelector("#entry-sheet").hidden = true;
  document.body.style.overflow = "";
  state.selectedEntry = null;
  state.reviewEvents = [];
  state.editingSection = null;
}

function bindActivityControls() {
  document.querySelector("#refresh-activity").addEventListener("click", loadActivity);
}

async function loadActivity() {
  const list = document.querySelector("#activity-list");
  list.innerHTML = loadingMarkup("Cargando actividad");
  refreshIcons();
  try {
    const [events, summary] = await Promise.all([api("/api/activity"), api("/api/activity/summary")]);
    renderActivity(events, summary);
  } catch (error) {
    list.innerHTML = errorMarkup(error.message);
    refreshIcons();
  }
}

function renderActivity(events, summary) {
  document.querySelector("#activity-summary").innerHTML = `
    <div class="summary-cell"><strong>${summary.total || 0}</strong><span>Eventos registrados</span></div>
    <div class="summary-cell"><strong>${summary.by_type?.inbox_created || 0}</strong><span>Entradas creadas</span></div>`;
  const list = document.querySelector("#activity-list");
  if (!events.length) {
    list.innerHTML = emptyMarkup("activity", "Todavía no hay actividad registrada");
  } else {
    list.innerHTML = events.map((event) => `
      <div class="activity-item"><span class="activity-icon"><i data-lucide="${eventIcons[event.event_type] || "activity"}"></i></span>
        <div class="activity-body"><strong>${escapeHtml(eventLabels[event.event_type] || formatPlainToken(event.event_type))}</strong><time>${formatDate(event.occurred_at, true)}</time></div>
      </div>`).join("");
  }
  refreshIcons();
}

async function checkConnection() {
  const status = document.querySelector("#connection-status");
  const label = document.querySelector("#connection-label");
  try {
    const [, options] = await Promise.all([api("/api/health"), api("/api/connection-options")]);
    state.connection = {
      mode: options.mode,
      lanUrl: options.lan_url,
      internetUrl: options.internet_url,
    };
    status.className = "connection is-online";
    label.textContent = options.mode === "lan" ? "LAN" : options.mode === "internet" ? "Internet" : "En red";
    status.title = options.mode === "lan" ? "Conexión directa por red local" : options.mode === "internet" ? "Conexión remota mediante Cloudflare" : "Conexión activa";
    renderConnectionSelector();
  } catch (_error) {
    status.className = "connection is-offline";
    label.textContent = "Sin conexión";
    renderConnectionSelector();
  }
}

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(options.headers || {}) }, ...options });
  let payload = null;
  try { payload = await response.json(); } catch (_error) { payload = null; }
  if (!response.ok) {
    const detail = payload?.detail;
    const error = new Error(typeof detail === "string" ? detail : detail?.message || `Error ${response.status}`);
    error.detail = detail;
    throw error;
  }
  return payload;
}

function renderDetectedData(entry, compact = false) {
  const dryRun = entry.dry_run || {};
  const detected = dryRun.detected_data || {};
  const items = detected.items || [];
  const observations = detected.stock_observations || [];
  const tasks = dryRun.suggested_tasks || [];
  if (!items.length && !observations.length && !tasks.length && detected.total_inferido == null) return "";
  const rows = [
    ...items.map((item) => `<div class="detected-row"><div class="detected-row-main"><strong>${escapeHtml(item.producto || "Producto pendiente")}</strong><span>${escapeHtml(formatQuantity(item.cantidad, item.unidad))}</span></div><div class="detected-row-value">${item.precio_unitario != null ? `<strong>${formatMoney(item.precio_unitario)}</strong><span>unitario</span>` : "<span>Sin precio</span>"}</div></div>`),
    ...observations.map((item) => `<div class="detected-row"><div class="detected-row-main"><strong>${escapeHtml(item.producto || "Producto pendiente")}</strong><span>${escapeHtml(formatQuantity(item.bolsas_estimadas_restantes, "bolsa(s) estimadas"))}</span></div><div class="detected-row-value">${item.kg_estimados_restantes != null ? `<strong>${escapeHtml(String(item.kg_estimados_restantes))} kg</strong><span>estimados</span>` : ""}</div></div>`),
    ...tasks.map((task) => `<div class="detected-row"><div class="detected-row-main"><strong>${escapeHtml(task.titulo || "Tarea sugerida")}</strong><span>${formatToken(task.estado)}</span></div></div>`),
  ].join("");
  return `<section class="detected-section ${compact ? "is-compact" : ""}"><div class="section-heading-row"><h3>Datos detectados</h3><span class="information-badge">Análisis inicial</span></div><div class="detected-rows">${rows}</div>${detected.total_inferido != null ? `<div class="detected-total"><span>Total calculado</span><strong>${formatMoney(detected.total_inferido, detected.moneda || "PYG")}</strong></div>` : ""}</section>`;
}

function purchaseField(name, label, type, value, required, placeholder = "") {
  return `<label class="field" data-field-path="${name}"><span>${label} ${required ? "<em>Obligatorio</em>" : "<em>Opcional</em>"}</span><input id="purchase-${name}" type="${type}" value="${escapeHtml(value || "")}" placeholder="${escapeHtml(placeholder)}" /></label>`;
}

function purchaseItemMarkup(item = {}, index = 0, totalItems = 1) {
  return `<article class="purchase-item" data-item-index="${index}"><div class="purchase-item-header"><strong>Producto ${index + 1}</strong><button class="item-remove-button" type="button" title="Quitar producto" ${totalItems <= 1 ? "disabled" : ""}><i data-lucide="trash-2"></i><span class="sr-only">Quitar producto</span></button></div><div class="field-grid item-field-grid"><label class="field field-wide" data-field-path="items.${index}.producto"><span>Producto <em>Obligatorio</em></span><input data-item-field="producto" type="text" value="${escapeHtml(item.producto || "")}" /></label><label class="field" data-field-path="items.${index}.cantidad"><span>Cantidad <em>Obligatorio</em></span><input data-item-field="cantidad" type="number" min="0" step="0.01" value="${escapeHtml(item.cantidad ?? "")}" /></label><label class="field" data-field-path="items.${index}.unidad"><span>Unidad <em>Obligatorio</em></span><input data-item-field="unidad" type="text" value="${escapeHtml(item.unidad || "")}" /></label><label class="field field-wide"><span>Precio unitario <em>Opcional</em></span><input data-item-field="precio_unitario" type="number" min="0" step="1" value="${escapeHtml(item.precio_unitario ?? "")}" /></label></div><div class="item-subtotal"><span>Subtotal</span><strong>${formatMoney(item.subtotal_inferido)}</strong></div></article>`;
}

function bindPurchaseItemEvents() {
  document.querySelectorAll(".purchase-item").forEach((item) => {
    if (item.dataset.eventsBound === "true") return;
    item.dataset.eventsBound = "true";
    item.querySelector(".item-remove-button")?.addEventListener("click", () => { item.remove(); renumberPurchaseItems(); updatePurchaseTotals(); });
    item.querySelectorAll("input").forEach((input) => input.addEventListener("input", updatePurchaseTotals));
  });
}

function addPurchaseItem() {
  const container = document.querySelector("#purchase-items");
  const index = container.querySelectorAll(".purchase-item").length;
  container.insertAdjacentHTML("beforeend", purchaseItemMarkup({}, index, index + 1));
  renumberPurchaseItems();
  bindPurchaseItemEvents();
  refreshIcons();
}

function renumberPurchaseItems() {
  const items = [...document.querySelectorAll(".purchase-item")];
  items.forEach((item, index) => {
    item.dataset.itemIndex = index;
    item.querySelector(".purchase-item-header strong").textContent = `Producto ${index + 1}`;
    item.querySelectorAll("[data-field-path]").forEach((field) => { field.dataset.fieldPath = field.dataset.fieldPath.replace(/items\.\d+\./, `items.${index}.`); });
    item.querySelector(".item-remove-button").disabled = items.length <= 1;
  });
}

function updatePurchaseTotals() {
  let total = 0;
  let hasPrice = false;
  document.querySelectorAll(".purchase-item").forEach((item) => {
    const quantity = Number(item.querySelector('[data-item-field="cantidad"]').value || 0);
    const price = Number(item.querySelector('[data-item-field="precio_unitario"]').value || 0);
    const subtotal = quantity * price;
    if (price > 0) hasPrice = true;
    item.querySelector(".item-subtotal strong").textContent = price > 0 ? formatMoney(subtotal) : "Pendiente";
    total += subtotal;
  });
  document.querySelector("#purchase-total").textContent = hasPrice ? formatMoney(total) : "Pendiente";
}

function calculateItemsTotal(items) {
  const priced = items.filter((item) => item.subtotal_inferido != null);
  return priced.length ? priced.reduce((total, item) => total + Number(item.subtotal_inferido), 0) : null;
}

function calculatePurchaseTotals(items, discount) {
  const subtotal = calculateItemsTotal(items);
  if (subtotal == null) return { subtotal: null, discountAmount: null, total: null };
  let discountAmount = 0;
  if (discount?.valor != null) {
    discountAmount = discount.tipo === "porcentaje"
      ? subtotal * Number(discount.valor) / 100
      : Number(discount.valor);
  }
  return { subtotal, discountAmount, total: subtotal - discountAmount };
}

function formatDiscount(discount) {
  if (!discount || discount.valor == null) return "-";
  return discount.tipo === "porcentaje" ? `${discount.valor}%` : formatMoney(discount.valor);
}

function loadingMarkup(label) { return `<div class="loading-state"><i class="spin" data-lucide="loader-circle"></i><span>${escapeHtml(label)}</span></div>`; }
function emptyMarkup(icon, label) { return `<div class="empty-state"><i data-lucide="${icon}"></i><span>${escapeHtml(label)}</span></div>`; }
function errorMarkup(message) { return `<div class="error-state"><i data-lucide="circle-alert"></i><span>${escapeHtml(message)}</span></div>`; }

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => { toast.hidden = true; }, 3200);
}

function hideToast() {
  clearTimeout(state.toastTimer);
  document.querySelector("#toast").hidden = true;
}

function reviewStatusLabel(entry) { return escapeHtml(reviewStatusLabels[entry.review_status] || entry.review_status || "Pendiente"); }
function formatPlainToken(value) { return String(value || "-").replaceAll("_", " ").replaceAll("-", " "); }
function formatToken(value) { return escapeHtml(formatPlainToken(value)); }
function formatQuantity(quantity, unit) {
  let displayUnit = unit || "";
  if (quantity !== 1 && ["bolsa", "unidad", "bandeja"].includes(displayUnit)) displayUnit += "s";
  return `${quantity == null ? "-" : new Intl.NumberFormat("es-PY").format(quantity)} ${displayUnit}`.trim();
}
function formatMoney(value, currency = "PYG") { return value == null || value === "" ? "Pendiente" : new Intl.NumberFormat("es-PY", { style: "currency", currency, maximumFractionDigits: 0 }).format(Number(value)); }
function formatDateOnly(value) { const [year, month, day] = String(value).split("-"); return year && month && day ? `${day}/${month}/${year}` : value; }
function formatDate(value, includeTime = false) { if (!value) return "-"; const date = new Date(value); return Number.isNaN(date.getTime()) ? escapeHtml(value) : new Intl.DateTimeFormat("es-PY", { day: "2-digit", month: "short", ...(includeTime ? { hour: "2-digit", minute: "2-digit" } : {}) }).format(date); }
function escapeHtml(value) { return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;"); }
