const loadingState = document.getElementById("loading-state");
const emptyState = document.getElementById("empty-state");
const linksContainer = document.getElementById("links-container");
const lastUpdatedEl = document.getElementById("last-updated");
const cardTemplate = document.getElementById("link-card-template");

async function loadLinks() {
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
    showError(error.message || "Failed to load links.");
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

  for (const link of links) {
    const card = createLinkCard(link);
    linksContainer.appendChild(card);
  }
}

function createLinkCard(link) {
  const fragment = cardTemplate.content.cloneNode(true);

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

  const preview = messageText.length > 100 ? `${messageText.slice(0, 100)}...` : messageText;
  messageEl.textContent = preview || "No message preview available.";

  copyBtn.addEventListener("click", async () => {
    await copyToClipboard(url, copyBtn);
  });

  return fragment;
}

async function copyToClipboard(url, button) {
  if (!url) {
    createToast("No URL to copy");
    return;
  }

  try {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      throw new Error("Clipboard API unsupported");
    }

    button.disabled = true;
    await navigator.clipboard.writeText(url);
    createToast("Link copied!");
  } catch (error) {
    fallbackCopyToClipboard(url);
  } finally {
    setTimeout(() => {
      button.disabled = false;
    }, 350);
  }
}

function fallbackCopyToClipboard(text) {
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

    createToast(success ? "Link copied!" : "Copy failed");
  } catch (_) {
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

  const diffMs = Date.now() - postedDate.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes === 1 ? "" : "s"} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? "" : "s"} ago`;
  if (diffDays === 1) return "Yesterday";
  return `${diffDays} days ago`;
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

function showLoading(visible) {
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
  errorCard.textContent = `Error: ${message}`;
  linksContainer.appendChild(errorCard);
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
