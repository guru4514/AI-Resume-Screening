const candidateList = document.getElementById("candidate-list");
const candidateTemplate = document.getElementById("candidate-template");
const analysisForm = document.getElementById("analysis-form");
const leaderboard = document.getElementById("leaderboard");
const statusBanner = document.getElementById("status-banner");
const resultSubtitle = document.getElementById("result-subtitle");
const comparisonPicker = document.getElementById("comparison-picker");
const comparisonContent = document.getElementById("comparison-content");
const addCandidateButton = document.getElementById("add-candidate");
const textModeSection = document.getElementById("text-mode-section");
const fileModeSection = document.getElementById("file-mode-section");
const resumeFilesInput = document.getElementById("resume-files");
const dropZone = document.getElementById("drop-zone");
const uploadPreview = document.getElementById("upload-preview");
const previewStatus = document.getElementById("preview-status");
const profilePreviewCards = document.getElementById("profile-preview-cards");
const modeInputs = Array.from(document.querySelectorAll('input[name="analysis-mode"]'));

let latestCandidates = [];
let selectedFiles = [];
const DEFAULT_API_BASE = "http://127.0.0.1:8001";
const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"];

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function isAllowedFile(file) {
  const name = (file.name || "").toLowerCase();
  return ALLOWED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

function getApiBaseUrl() {
  const explicitBase = window.localStorage.getItem("talentrank_api_base");
  if (explicitBase) {
    return explicitBase.replace(/\/$/, "");
  }

  if (window.location.protocol === "file:") {
    return DEFAULT_API_BASE;
  }

  return window.location.origin;
}

function apiUrl(path) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${getApiBaseUrl()}${normalizedPath}`;
}

async function parseApiResponse(response) {
  const rawBody = await response.text();
  const contentType = (response.headers.get("content-type") || "").toLowerCase();

  if (contentType.includes("application/json")) {
    if (!rawBody) {
      return {};
    }

    try {
      return JSON.parse(rawBody);
    } catch {
      throw new Error("API returned invalid JSON.");
    }
  }

  const preview = rawBody.replace(/\s+/g, " ").trim().slice(0, 180);
  if (!response.ok) {
    throw new Error(
      `API returned non-JSON response (${response.status} ${response.statusText}). ${preview || "No response body."}`
    );
  }

  throw new Error(
    `Expected JSON response from API, but got '${contentType || "unknown content type"}'. Check backend URL/origin.`
  );
}

function getAnalysisMode() {
  const selected = modeInputs.find((input) => input.checked);
  return selected ? selected.value : "text";
}

function updateModeVisibility() {
  const mode = getAnalysisMode();
  const isTextMode = mode === "text";

  textModeSection.classList.toggle("hidden-mode", !isTextMode);
  fileModeSection.classList.toggle("hidden-mode", isTextMode);
  addCandidateButton.classList.toggle("hidden-mode", !isTextMode);
}

function updateUploadPreview() {
  if (!selectedFiles.length) {
    uploadPreview.className = "upload-preview empty-state";
    uploadPreview.innerHTML = "<p>No files selected.</p>";
    profilePreviewCards.className = "profile-preview-cards empty-state";
    profilePreviewCards.innerHTML = "<p>Parsed profile previews will appear here.</p>";
    previewStatus.classList.add("hidden");
    return;
  }

  uploadPreview.className = "upload-preview";
  uploadPreview.innerHTML = `
    <p><strong>${selectedFiles.length}</strong> file(s) selected</p>
    <ul>${selectedFiles.map((file) => `<li>${escapeHtml(file.name)}</li>`).join("")}</ul>
  `;
}

function syncInputWithSelectedFiles() {
  const transfer = new DataTransfer();
  selectedFiles.forEach((file) => transfer.items.add(file));
  resumeFilesInput.files = transfer.files;
}

function setSelectedFiles(files) {
  selectedFiles = files;
  syncInputWithSelectedFiles();
  updateUploadPreview();
  void fetchUploadPreviews();
}

function fileFingerprint(file) {
  return `${file.name}::${file.size}::${file.lastModified}`;
}

function mergeSelectedFiles(incomingFiles) {
  if (!incomingFiles.length) {
    return selectedFiles;
  }

  const validFiles = incomingFiles.filter((file) => {
    if (!isAllowedFile(file)) {
      console.warn(`Skipped unsupported file: ${file.name}`);
      return false;
    }
    return true;
  });

  const byFingerprint = new Map();
  selectedFiles.forEach((file) => {
    byFingerprint.set(fileFingerprint(file), file);
  });

  validFiles.forEach((file) => {
    byFingerprint.set(fileFingerprint(file), file);
  });

  return Array.from(byFingerprint.values());
}

function renderProfilePreviews(previews) {
  if (!previews.length) {
    profilePreviewCards.className = "profile-preview-cards empty-state";
    profilePreviewCards.innerHTML = "<p>Parsed profile previews will appear here.</p>";
    return;
  }

  profilePreviewCards.className = "profile-preview-cards";
  profilePreviewCards.innerHTML = previews
    .map((preview) => {
      if (preview.status === "error") {
        return `
          <article class="profile-card error">
            <h4>${escapeHtml(preview.file_name)}</h4>
            <p class="profile-meta">Status: parse failed</p>
            <p>${escapeHtml(preview.message || "Could not parse this file.")}</p>
          </article>
        `;
      }

      const skills = (preview.detected_skills || []).map((skill) => `<span class="pill">${escapeHtml(skill)}</span>`).join("");
      return `
        <article class="profile-card">
          <h4>${escapeHtml(preview.candidate_name || preview.file_name)}</h4>
          <p class="profile-meta">${escapeHtml(preview.file_name)} | ${preview.years_experience ?? 0} years detected</p>
          <div class="pill-row">${skills || "<span class='pill'>No skill keywords detected</span>"}</div>
        </article>
      `;
    })
    .join("");
}

async function fetchUploadPreviews() {
  if (!selectedFiles.length) {
    return;
  }

  previewStatus.classList.remove("hidden");
  previewStatus.textContent = "Parsing uploaded resumes...";

  const formData = new FormData();
  selectedFiles.forEach((file) => {
    formData.append("resumes", file, file.name);
  });

  try {
    const response = await fetch(apiUrl("/v1/preview-files"), {
      method: "POST",
      body: formData,
    });

    const data = await parseApiResponse(response);
    if (!response.ok) {
      throw new Error(data.detail || "Preview parsing failed");
    }

    renderProfilePreviews(data.previews || []);
    previewStatus.textContent = "Preview ready. Parsed candidate profiles from uploaded resumes.";
  } catch (error) {
    profilePreviewCards.className = "profile-preview-cards empty-state";
    profilePreviewCards.innerHTML = "<p>Unable to parse preview right now.</p>";
    const message = error && error.message ? error.message : String(error);
    previewStatus.textContent = `Preview error: ${message}`;
  }
}

function splitCommaValues(value) {
  return value
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
}

function addCandidate(data = {}) {
  const clone = candidateTemplate.content.cloneNode(true);
  const item = clone.querySelector(".candidate-item");

  item.querySelector(".candidate-name").value = data.name || "";
  item.querySelector(".candidate-years").value = data.years_experience || "";
  item.querySelector(".candidate-resume").value = data.resume_text || "";

  item.querySelector(".remove-candidate").addEventListener("click", () => {
    item.remove();
  });

  candidateList.appendChild(clone);
}

function collectCandidates() {
  const items = Array.from(candidateList.querySelectorAll(".candidate-item"));

  return items.map((item) => ({
    name: item.querySelector(".candidate-name").value.trim(),
    years_experience: Number(item.querySelector(".candidate-years").value || 0),
    resume_text: item.querySelector(".candidate-resume").value.trim(),
  }));
}

function updateRoleFamilyVisibility() {
  const roleFamilySelect = document.getElementById("role-family");
  const customRoleInput = document.getElementById("custom-role-family");
  const isOther = roleFamilySelect.value === "other";
  customRoleInput.classList.toggle("hidden", !isOther);
  if (isOther) {
    customRoleInput.focus();
  }
}

function collectFormContext() {
  const roleFamilySelect = document.getElementById("role-family");
  const customRoleInput = document.getElementById("custom-role-family");
  const roleFamily = roleFamilySelect.value === "other"
    ? customRoleInput.value.trim()
    : roleFamilySelect.value;

  return {
    jobTitle: document.getElementById("job-title").value.trim(),
    roleFamily,
    jobDescription: document.getElementById("job-description").value.trim(),
    mustHaveInput: document.getElementById("must-have").value,
    niceToHaveInput: document.getElementById("nice-to-have").value,
  };
}

function validateTextCandidates(candidates) {
  if (!candidates.length) {
    return "Add at least one candidate.";
  }

  const hasInvalidCandidate = candidates.some(
    (candidate) => !candidate.name || !candidate.resume_text
  );
  if (hasInvalidCandidate) {
    return "Please provide complete data for all text candidates.";
  }

  return null;
}

function validateFileCandidates(files) {
  if (!files.length) {
    return "Upload at least one resume file.";
  }

  return null;
}

async function runTextAnalysis(context) {
  const payload = {
    job_title: context.jobTitle,
    role_family: context.roleFamily,
    job_description: context.jobDescription,
    must_have_skills: splitCommaValues(context.mustHaveInput),
    nice_to_have_skills: splitCommaValues(context.niceToHaveInput),
    candidates: collectCandidates(),
  };

  const validationError = validateTextCandidates(payload.candidates);
  if (validationError) {
    throw new Error(validationError);
  }

  return fetch(apiUrl("/v1/analyze"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

async function runFileAnalysis(context) {
  const validationError = validateFileCandidates(selectedFiles);
  if (validationError) {
    throw new Error(validationError);
  }

  const formData = new FormData();
  formData.append("job_title", context.jobTitle);
  formData.append("role_family", context.roleFamily);
  formData.append("job_description", context.jobDescription);
  formData.append("must_have_skills", context.mustHaveInput);
  formData.append("nice_to_have_skills", context.niceToHaveInput);

  selectedFiles.forEach((file) => {
    formData.append("resumes", file, file.name);
  });

  return fetch(apiUrl("/v1/analyze-files"), {
    method: "POST",
    body: formData,
  });
}

function setStatus(type, message) {
  statusBanner.classList.remove("hidden", "success", "error");
  statusBanner.classList.add(type === "error" ? "error" : "success");
  statusBanner.textContent = message;
}

function scoreBar(label, value) {
  const safe = Math.max(0, Math.min(100, value));
  return `
    <div class="score-row">
      <span>${label}</span>
      <div class="score-bar"><div class="score-fill" style="width: ${safe}%"></div></div>
      <strong>${safe.toFixed(1)}</strong>
    </div>
  `;
}

function renderLeaderboard(candidates) {
  if (!candidates.length) {
    leaderboard.className = "leaderboard empty-state";
    leaderboard.innerHTML = "<p>No candidates returned from analysis.</p>";
    return;
  }

  leaderboard.className = "leaderboard";
  leaderboard.innerHTML = candidates
    .map((candidate, index) => {
      const hardClass = candidate.hard_constraint_passed ? "good" : "warn";
      const hardLabel = candidate.hard_constraint_passed ? "Hard Constraint Passed" : "Hard Constraint Risk";

      return `
        <article class="candidate-card" style="animation-delay:${index * 80}ms">
          <div class="candidate-top">
            <h3>${escapeHtml(candidate.name)}</h3>
            <span class="badge ${hardClass}">${hardLabel}</span>
          </div>
          ${scoreBar("Total", candidate.total_score)}
          ${scoreBar("Required Skill", candidate.skill_score)}
          ${scoreBar("Must-Have", candidate.must_have_match_rate)}
          ${scoreBar("Nice-To-Have", candidate.nice_to_have_match_rate)}
          ${scoreBar("Experience", candidate.experience_score)}
          ${scoreBar("Role Fit", candidate.role_fit_score)}
          <div>
            <strong>Matched Skills:</strong>
            <div class="pill-row">${candidate.matched_skills.map((skill) => `<span class="pill">${escapeHtml(skill)}</span>`).join("") || "<span class='pill'>none</span>"}</div>
          </div>
          <div>
            <strong>Missing Skills:</strong>
            <div class="pill-row">${candidate.missing_skills.map((skill) => `<span class="pill miss">${escapeHtml(skill)}</span>`).join("") || "<span class='pill'>none</span>"}</div>
          </div>
        </article>
      `;
    })
    .join("");
}

function fillComparisonSelects(candidates) {
  latestCandidates = candidates;
  const maxCompare = 10;
  const available = candidates.slice(0, maxCompare);

  comparisonPicker.innerHTML = available
    .map((candidate, idx) => {
      const checked = idx < Math.min(available.length, maxCompare) ? "checked" : "";
      return `
        <label class="compare-checkbox">
          <input type="checkbox" value="${idx}" ${checked} />
          <span>${escapeHtml(candidate.name)}</span>
        </label>
      `;
    })
    .join("");

  comparisonPicker.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    checkbox.addEventListener("change", renderComparison);
  });

  renderComparison();
}

function compareCard(candidate, index) {
  const semanticRows = Object.entries(candidate.semantic_matches || {})
    .map(([target, support]) => `<li>${escapeHtml(target)}: ${support.map(escapeHtml).join(", ")}</li>`)
    .join("");

  return `
    <article class="compare-card" style="animation-delay:${index * 60}ms">
      <h4>${escapeHtml(candidate.name)}</h4>
      ${scoreBar("Total", candidate.total_score)}
      ${scoreBar("Skill", candidate.skill_score)}
      ${scoreBar("Must-Have", candidate.must_have_match_rate)}
      ${scoreBar("Nice-To-Have", candidate.nice_to_have_match_rate)}
      ${scoreBar("Experience", candidate.experience_score)}
      ${scoreBar("Role Fit", candidate.role_fit_score)}
      <p><strong>Strengths:</strong> ${(candidate.strengths || []).map(escapeHtml).join(" | ") || "None"}</p>
      <p><strong>Concerns:</strong> ${(candidate.concerns || []).map(escapeHtml).join(" | ") || "None"}</p>
      <p><strong>Semantic Evidence:</strong></p>
      <ul>${semanticRows || "<li>None</li>"}</ul>
    </article>
  `;
}

function renderComparison() {
  const checkedBoxes = Array.from(comparisonPicker.querySelectorAll('input[type="checkbox"]:checked'));
  const selectedIndices = checkedBoxes.map((cb) => Number(cb.value));
  const selectedCandidates = selectedIndices
    .map((idx) => latestCandidates[idx])
    .filter(Boolean);

  if (!selectedCandidates.length) {
    comparisonContent.className = "comparison-content empty-state";
    comparisonContent.innerHTML = "<p>Select at least one candidate to compare.</p>";
    return;
  }

  comparisonContent.className = "comparison-content";
  comparisonContent.innerHTML = `<div class="compare-grid">${selectedCandidates.map((c, i) => compareCard(c, i)).join("")}</div>`;
}

addCandidateButton.addEventListener("click", () => addCandidate());
document.getElementById("role-family").addEventListener("change", updateRoleFamilyVisibility);

modeInputs.forEach((modeInput) => {
  modeInput.addEventListener("change", updateModeVisibility);
});
resumeFilesInput.addEventListener("change", () => {
  const incomingFiles = Array.from(resumeFilesInput.files || []);
  setSelectedFiles(mergeSelectedFiles(incomingFiles));
});

dropZone.addEventListener("click", () => {
  resumeFilesInput.click();
});

dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    resumeFilesInput.click();
  }
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("active");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("active");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("active");
  const incomingFiles = Array.from(event.dataTransfer?.files || []);
  if (!incomingFiles.length) {
    return;
  }
  setSelectedFiles(mergeSelectedFiles(incomingFiles));
});

analysisForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  setStatus("success", "Running analysis...");

  try {
    const mode = getAnalysisMode();
    const context = collectFormContext();
    const response = mode === "files"
      ? await runFileAnalysis(context)
      : await runTextAnalysis(context);

    const data = await parseApiResponse(response);

    if (!response.ok) {
      throw new Error(data.detail || "Analysis request failed");
    }

    resultSubtitle.textContent = `${data.job_title} | role profile: ${data.role_family}`;
    renderLeaderboard(data.ranked_candidates || []);
    fillComparisonSelects(data.ranked_candidates || []);
    setStatus("success", "Analysis complete. Leaderboard refreshed.");
  } catch (error) {
    const baseMessage = error && error.message ? error.message : String(error);
    if (baseMessage.toLowerCase().includes("failed to fetch")) {
      setStatus(
        "error",
        "Error: Failed to reach API. Start backend with uvicorn and open dashboard at the same origin or set localStorage talentrank_api_base."
      );
      return;
    }

    setStatus("error", `Error: ${baseMessage}`);
  }
});

addCandidate({
  name: "Aman",
  years_experience: 4,
  resume_text:
    "Python, FastAPI, AWS, Docker, PostgreSQL, API optimization, monitoring, CI/CD",
});
addCandidate({
  name: "Riya",
  years_experience: 3,
  resume_text:
    "Django, Azure, Kubernetes, Terraform, SQL, backend service integrations, observability",
});
addCandidate({
  name: "Nikhil",
  years_experience: 5,
  resume_text:
    "Java Spring, microservices, AWS, Docker, Jenkins, PostgreSQL, incident response",
});

  updateModeVisibility();
  updateUploadPreview();
