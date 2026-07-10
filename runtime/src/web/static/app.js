const state = {
  currentView: "capture",
  inboxFilter: "all",
  selectedEntry: null,
  reviewEvents: [],
  editingSection: null,
  toastTimer: null,
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
  bindSheetControls();
  checkConnection();
  refreshInboxSummary();
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
  window.scrollTo({ top: 0, behavior: "smooth" });
  refreshIcons();
}

function bindCaptureForm() {
  const form = document.querySelector("#capture-form");
  const message = document.querySelector("#message");
  message.addEventListener("input", () => {
    document.querySelector("#message-count").textContent = message.value.length.toLocaleString("es-PY");
  });
  form.addEventListener("submit", captureEntry);
}

async function captureEntry(event) {
  event.preventDefault();
  const message = document.querySelector("#message");
  const context = document.querySelector("#context");
  const submit = document.querySelector("#capture-submit");
  const originalLabel = submit.innerHTML;
  submit.disabled = true;
  submit.innerHTML = '<i class="spin" data-lucide="loader-circle"></i><span>Procesando</span>';
  refreshIcons();
  try {
    const entry = await api("/api/inbox", {
      method: "POST",
      body: JSON.stringify({ message: message.value, context: context.value || null }),
    });
    renderCaptureResult(entry);
    message.value = "";
    context.value = "";
    document.querySelector("#message-count").textContent = "0";
    document.querySelector(".context-panel").open = false;
    showToast("Entrada guardada en el inbox");
    await refreshInboxSummary();
  } catch (error) {
    showToast(error.message || "No se pudo guardar la entrada");
  } finally {
    submit.disabled = false;
    submit.innerHTML = originalLabel;
    refreshIcons();
  }
}

function renderCaptureResult(entry) {
  const result = document.querySelector("#capture-result");
  const classification = entry.classification;
  const missing = entry.missing_data || [];
  result.hidden = false;
  result.innerHTML = `
    <div class="result-header">
      <div><p class="eyebrow">${reviewStatusLabel(entry)}</p><h2>Entrada guardada</h2></div>
      <span class="result-check"><i data-lucide="check"></i></span>
    </div>
    <div class="result-grid">
      <div class="result-metric"><span>Intención</span><strong>${formatToken(classification.intent)}</strong></div>
      <div class="result-metric"><span>Dominio</span><strong>${formatToken(classification.primary_domain)}</strong></div>
      <div class="result-metric"><span>Riesgo</span><strong>${escapeHtml(classification.risk_level)}</strong></div>
      <div class="result-metric"><span>Confirmación</span><strong>${classification.requires_confirmation ? "Requerida" : "No requerida"}</strong></div>
    </div>
    ${renderDetectedData(entry, true)}
    ${missing.length ? `<div class="missing-block"><h3>Datos por completar o verificar</h3><ul>${missing.slice(0, 5).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
  `;
  refreshIcons();
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
    await api("/api/health");
    status.className = "connection is-online";
    label.textContent = "En red";
  } catch (_error) {
    status.className = "connection is-offline";
    label.textContent = "Sin conexión";
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
