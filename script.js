const loadingState = document.getElementById("loading-state");
const emptyState = document.getElementById("empty-state");
const linksContainer = document.getElementById("links-container");
const lastUpdatedEl = document.getElementById("last-updated");
const cardTemplate = document.getElementById("link-card-template");
const copyResetTimers = new WeakMap();

async function loadLinks() {
  renderLoadingState();
  showLoading(true);
  setEmptyHidden(true);

  try {
    const response = await fetch("data.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Failed to load data.json (HTTP ${response.status})`);
    }

    let data;
    try {
      data = await response.json();
    } catch (jsonError) {
      throw new Error("Malformed JSON in data.json");
    }

    displayLinks(data);
    updateTimestamp(data?.timestamp);
  } catch (error) {
    showError(error);
    updateTimestamp(null);
  } finally {
    showLoading(false);
  }
}

function displayLinks(data) {
  linksContainer.innerHTML = "";

  const links = Array.isArray(data?.links) ? [...data.links] : [];
  links.sort((a, b) => new Date(b.posted_time || 0) - new Date(a.posted_time || 0));

  if (links.length === 0) {
    setEmptyHidden(false);
    return;
  }

  setEmptyHidden(true);

  links.forEach((link, index) => {
    const card = createLinkCard(link, index);
    linksContainer.appendChild(card);
  });
}

function createLinkCard(link, index = 0) {
  const fragment = cardTemplate.content.cloneNode(true);

  const cardEl = fragment.querySelector(".link-card");
  const urlEl = fragment.querySelector(".link-url");
  const channelEl = fragment.querySelector(".source-channel");
  const postedTimeEl = fragment.querySelector(".posted-time");
  const messageEl = fragment.querySelector(".message-preview");
  const copyBtn = fragment.querySelector(".copy-btn");

  const url = link?.url || "";
  const channelName = link?.source_channel_name || String(link?.source_channel_id || "Unknown");
  const postedTime = link?.posted_time || null;
  const messageText = typeof link?.message_text === "string" ? link.message_text : "";

  urlEl.href = url || "#";
  urlEl.textContent = url || "Invalid URL";

  channelEl.textContent = channelName;
  channelEl.setAttribute("title", `Channel ID: ${link?.source_channel_id ?? "N/A"}`);

  postedTimeEl.textContent = formatRelativeTime(postedTime);
  postedTimeEl.dateTime = postedTime || "";
  postedTimeEl.title = formatAbsoluteTime(postedTime);

  const preview = messageText.length > 100 ? `${messageText.slice(0, 100)}...` : messageText;
  messageEl.textContent = preview || "No message preview available.";

  if (cardEl) {
    cardEl.style.animationDelay = `${Math.min(index * 80, 480)}ms`;
  }

  copyBtn.addEventListener("click", async () => {
    await copyToClipboard(url, copyBtn);
  });

  return fragment;
}

async function copyToClipboard(url, button) {
  if (!url) {
    setTemporaryButtonText(button, "No link");
    createToast("No URL to copy");
    return;
  }

  try {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      throw new Error("Clipboard API unsupported");
    }

    button.disabled = true;
    await navigator.clipboard.writeText(url);
    setTemporaryButtonText(button, "Copied!");
    createToast("Link copied!");
  } catch (error) {
    fallbackCopyToClipboard(url, button);
  } finally {
    setTimeout(() => {
      button.disabled = false;
    }, 350);
  }
}

function fallbackCopyToClipboard(text, button) {
  try {
    const helper = document.createElement("textarea");
    helper.value = text;
    helper.setAttribute("readonly", "");
    helper.style.position = "fixed";
    helper.style.opacity = "0";
    document.body.appendChild(helper);
    helper.select();
    const success = document.execCommand("copy");
    document.body.removeChild(helper);

    if (success) {
      setTemporaryButtonText(button, "Copied!");
    } else {
      setTemporaryButtonText(button, "Retry");
    }

    createToast(success ? "Link copied!" : "Copy failed");
  } catch (_) {
    setTemporaryButtonText(button, "Retry");
    createToast("Copy not supported on this browser");
  }
}

function formatRelativeTime(timestamp) {
  if (!timestamp) {
    return "Unknown time";
  }

  const postedDate = new Date(timestamp);
  if (Number.isNaN(postedDate.getTime())) {
    return "Unknown time";
  }

  const diffMs = Math.max(Date.now() - postedDate.getTime(), 0);
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffWeeks = Math.floor(diffDays / 7);

  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes === 1 ? "" : "s"} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? "" : "s"} ago`;
  if (diffWeeks < 5) return `${diffWeeks} week${diffWeeks === 1 ? "" : "s"} ago`;
  return `${diffDays} days ago`;
}

function formatAbsoluteTime(timestamp) {
  if (!timestamp) {
    return "Unknown time";
  }

  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) {
    return "Unknown time";
  }

  return parsed.toLocaleString("en-GB");
}

function createToast(message) {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.background = "#2d7d46";
  toast.style.color = "#ffffff";
  toast.style.padding = "10px 14px";
  toast.style.borderRadius = "8px";
  toast.style.boxShadow = "0 10px 20px rgba(0, 0, 0, 0.3)";
  toast.style.zIndex = "9999";
  toast.style.opacity = "0";
  toast.style.transform = "translateY(10px)";
  toast.style.transition = "opacity 0.25s ease, transform 0.25s ease";

  document.body.appendChild(toast);

  requestAnimationFrame(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";
  });

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    setTimeout(() => {
      toast.remove();
    }, 260);
  }, 2000);
}

function setTemporaryButtonText(button, text) {
  if (!button) {
    return;
  }

  const defaultLabel = button.dataset.defaultLabel || button.textContent || "Copy";
  button.dataset.defaultLabel = defaultLabel;
  button.textContent = text;

  const existingTimer = copyResetTimers.get(button);
  if (existingTimer) {
    clearTimeout(existingTimer);
  }

  const resetTimer = setTimeout(() => {
    button.textContent = defaultLabel;
    copyResetTimers.delete(button);
  }, 1600);

  copyResetTimers.set(button, resetTimer);
}

function showLoading(visible) {
  loadingState.setAttribute("aria-busy", visible ? "true" : "false");
  loadingState.hidden = !visible;
}

function setEmptyHidden(hidden) {
  emptyState.hidden = hidden;
}

function showError(message) {
  linksContainer.innerHTML = "";
  setEmptyHidden(true);

  const errorCard = document.createElement("section");
  errorCard.className = "state-card";
  errorCard.setAttribute("role", "alert");

  const title = document.createElement("p");
  title.textContent = "We couldn't load the latest cricket streams.";
  title.style.margin = "0 0 6px";
  title.style.fontWeight = "700";

  const detail = document.createElement("p");
  detail.textContent = getFriendlyErrorMessage(message);
  detail.style.margin = "0";

  errorCard.append(title, detail);
  linksContainer.appendChild(errorCard);
}

function getFriendlyErrorMessage(error) {
  const message = typeof error === "string" ? error : error?.message || "";

  if (message.includes("Malformed JSON")) {
    return "The stream list was received, but it could not be read correctly. Please try again shortly.";
  }

  if (message.includes("HTTP")) {
    return "The stream service is not responding right now. Please refresh in a moment.";
  }

  return "Please check your connection and try again. We'll keep the page ready for the next refresh.";
}

function renderLoadingState() {
  loadingState.replaceChildren();

  const label = document.createElement("p");
  label.textContent = "Loading latest cricket streams...";
  label.style.margin = "0 0 12px";
  label.style.fontWeight = "600";

  const skeletonWrap = document.createElement("div");
  skeletonWrap.style.display = "grid";
  skeletonWrap.style.gap = "10px";

  for (let index = 0; index < 3; index += 1) {
    const skeleton = document.createElement("div");
    skeleton.style.height = "12px";
    skeleton.style.width = index === 2 ? "72%" : "100%";
    skeleton.style.borderRadius = "999px";
    skeleton.style.background = "rgba(255, 255, 255, 0.08)";

    if (typeof skeleton.animate === "function") {
      skeleton.animate(
        [
          { opacity: 0.35 },
          { opacity: 0.75 },
          { opacity: 0.35 }
        ],
        {
          duration: 1100,
          delay: index * 120,
          iterations: Infinity,
          easing: "ease-in-out"
        }
      );
    }

    skeletonWrap.appendChild(skeleton);
  }

  loadingState.append(label, skeletonWrap);
}

function updateTimestamp(timestamp) {
  if (!timestamp) {
    lastUpdatedEl.textContent = "Unavailable";
    lastUpdatedEl.dateTime = "";
    return;
  }

  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) {
    lastUpdatedEl.textContent = "Unavailable";
    lastUpdatedEl.dateTime = "";
    return;
  }

  lastUpdatedEl.textContent = parsed.toLocaleString("en-GB");
  lastUpdatedEl.dateTime = parsed.toISOString();
}

document.addEventListener("DOMContentLoaded", () => {
  loadLinks();
  setInterval(loadLinks, 5 * 60 * 1000);
});
