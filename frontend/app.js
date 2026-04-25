async function testHealth() {
    const statusElement = document.getElementById("health");

    if (!statusElement) return;

    try {
        const response = await fetch("/health");
        const data = await response.json();

        statusElement.textContent = "Backend: " + data.status;
        statusElement.classList.remove("badge-error");
        statusElement.classList.add("badge-success");

        updateAdminStats({ healthText: "OK" });
    } catch (error) {
        statusElement.textContent = "Backend: erreur (serveur non démarré)";
        statusElement.classList.remove("badge-success");
        statusElement.classList.add("badge-error");

        updateAdminStats({ healthText: "Erreur" });
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const messageElement = document.getElementById("loginMessage");
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    messageElement.textContent = "";
    messageElement.style.color = "";

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            messageElement.textContent = data.message || "Erreur de connexion";
            messageElement.style.color = "red";
            return;
        }

        messageElement.textContent = data.message;
        messageElement.style.color = "green";

        showToast("Connexion réussie", "Redirection en cours...", "success");

        if (data.role === "ADMIN") {
            window.location.href = "/admin";
        } else {
            window.location.href = "/app";
        }

    } catch (error) {
        showToast("Connexion refusée", data.message || "Erreur de connexion", "error");
        messageElement.textContent = "Erreur de communication avec le serveur";
        messageElement.style.color = "red";
    }
}

function initLoginForm() {
    const loginForm = document.getElementById("loginForm");
    if (!loginForm) return;

    loginForm.addEventListener("submit", handleLogin);
}

// async function loadSessionInfo() {
//     const sessionInfo = document.getElementById("sessionInfo");
//     if (!sessionInfo) return;

//     try {
//         const response = await fetch("/auth/me");

//         if (!response.ok) {
//             window.location.href = "/login";
//             return;
//         }

//         const data = await response.json();
//         const user = data.user;

//         sessionInfo.textContent =
//             "Connecté en tant que " + user.username + " (" + user.role + ")";
//     } catch (error) {
//         sessionInfo.textContent = "Impossible de charger les informations de session";
//     }
// }

async function loadSessionInfo() {
    const sessionInfo = document.getElementById("sessionInfo");
    if (!sessionInfo) return;

    try {
        const response = await fetch("/auth/me");

        if (!response.ok) {
            window.location.href = "/login";
            return;
        }

        const data = await response.json();
        const user = data.user;

        sessionInfo.textContent = `${user.username} (${user.role})`;
        refreshAdminAvatar();
    } catch (error) {
        sessionInfo.textContent = "Session indisponible";
        refreshAdminAvatar();
    }
}

async function handleLogout() {
    try {
        await fetch("/auth/logout", {
            method: "POST"
        });

        window.location.href = "/login";
    } catch (error) {
        alert("Erreur lors de la déconnexion");
    }
}

function initLogoutButton() {
    const logoutBtn = document.getElementById("logoutBtn");
    if (!logoutBtn) return;

    logoutBtn.addEventListener("click", handleLogout);
}

async function loadDocuments() {
    const messageElement = document.getElementById("documentsMessage");
    const table = document.getElementById("documentsTable");
    const tableBody = document.getElementById("documentsTableBody");

    if (!messageElement || !table || !tableBody) return;

    try {
        const response = await fetch("/documents");

        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            messageElement.textContent = data.message || "Impossible de charger les documents";
            messageElement.style.color = "red";
            table.style.display = "none";
            updateAdminStats({ documentsCount: 0 });
            return;
        }

        const data = await response.json();
        const documents = data.documents || [];

        if (documents.length === 0) {
            messageElement.textContent = "Aucun document importé";
            messageElement.style.color = "";
            table.style.display = "none";
            tableBody.innerHTML = "";
            updateAdminStats({ documentsCount: 0 });
            return;
        }

        tableBody.innerHTML = "";

        documents.forEach(doc => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${doc.id}</td>
                <td>${doc.title}</td>
                <td>${doc.filename}</td>
                <td>${doc.file_type}</td>
                <td>${doc.imported_at}</td>
            `;

            tableBody.appendChild(row);
        });

        messageElement.textContent = "";
        messageElement.style.color = "";
        table.style.display = "table";
        updateAdminStats({ documentsCount: documents.length });

    } catch (error) {
        messageElement.textContent = "Erreur de communication avec le serveur";
        messageElement.style.color = "red";
        table.style.display = "none";
        updateAdminStats({ documentsCount: 0 });
    }
}

async function loadLogs() {
    const messageElement = document.getElementById("logsMessage");
    const table = document.getElementById("logsTable");
    const tableBody = document.getElementById("logsTableBody");

    if (!messageElement || !table || !tableBody) return;

    messageElement.textContent = "Chargement des logs...";
    messageElement.style.color = "";
    table.style.display = "none";
    tableBody.innerHTML = "";

    try {
        const response = await fetch("/logs?limit=50");
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            messageElement.textContent = data.message || "Impossible de charger les logs";
            messageElement.style.color = "red";
            updateAdminStats({ logsCount: 0 });
            return;
        }

        const logs = data.logs || [];

        if (logs.length === 0) {
            messageElement.textContent = "Aucun log disponible";
            messageElement.style.color = "";
            updateAdminStats({ logsCount: 0 });
            return;
        }

        logs.forEach(log => {
            const row = document.createElement("tr");

            const documentsText = Array.isArray(log.used_documents) && log.used_documents.length > 0
                ? log.used_documents.join(", ")
                : "Aucun document";

            row.innerHTML = `
                <td>${log.id}</td>
                <td>${log.username || "Inconnu"}</td>
                <td>${log.question}</td>
                <td>${documentsText}</td>
                <td>${log.created_at}</td>
            `;

            tableBody.appendChild(row);
        });

        messageElement.textContent = "";
        messageElement.style.color = "";
        table.style.display = "table";
        updateAdminStats({ logsCount: logs.length });

    } catch (error) {
        messageElement.textContent = "Erreur de communication avec le serveur";
        messageElement.style.color = "red";
        updateAdminStats({ logsCount: 0 });
    }
}

function initRefreshLogsButton() {
    const refreshBtn = document.getElementById("refreshLogsBtn");
    if (!refreshBtn) return;

    refreshBtn.addEventListener("click", loadLogs);
}

async function handleUpload(event) {
    event.preventDefault();

    const fileInput = document.getElementById("uploadFile");
    const uploadMessage = document.getElementById("uploadMessage");

    if (!fileInput || !uploadMessage) return;

    uploadMessage.textContent = "";
    uploadMessage.style.color = "";

    if (!fileInput.files || fileInput.files.length === 0) {
        uploadMessage.textContent = "Veuillez sélectionner un fichier.";
        uploadMessage.style.color = "red";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/documents/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            uploadMessage.textContent = data.message || "Erreur lors de l'upload.";
            uploadMessage.style.color = "red";
            return;
        }

        uploadMessage.textContent =
            data.message || "Fichier uploadé, ingéré et indexé avec succès.";
        uploadMessage.style.color = "green";

        fileInput.value = "";

        const fileName = document.getElementById("uploadFileName");
        const dropzone = document.getElementById("uploadDropzone");

        if (fileName) fileName.textContent = "Aucun fichier sélectionné";
        if (dropzone) dropzone.classList.remove("has-file");
        showToast("Upload réussi", "Le document a été ajouté et indexé automatiquement.", "success");

        await loadDocuments();
        await loadLogs();

    } catch (error) {
        showToast("Échec de l'upload", data.message || "Erreur lors de l'upload.", "error");
        uploadMessage.textContent = "Erreur de communication avec le serveur.";
        uploadMessage.style.color = "red";
    }
}

function getCurrentTimeLabel() {
    const now = new Date();
    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function getUserInitial() {
    const sessionInfo = document.getElementById("sessionInfo");
    if (!sessionInfo || !sessionInfo.textContent) return "U";

    const text = sessionInfo.textContent.trim();
    const match = text.match(/tant que\s+([^\s]+)/i);
    if (match && match[1]) {
        return match[1].charAt(0).toUpperCase();
    }

    return "U";
}

function syncUserAvatar() {
    const avatar = document.getElementById("userAvatar");
    if (!avatar) return;
    avatar.textContent = getUserInitial();
}

function autoResizeTextarea() {
    const input = document.getElementById("questionInput");
    if (!input) return;

    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 180) + "px";
}

function hideWelcomePanel() {
    const welcomePanel = document.getElementById("welcomePanel");
    if (welcomePanel) {
        welcomePanel.classList.add("hidden");
    }
}

function clearQueryMessage() {
    const queryMessage = document.getElementById("queryMessage");
    if (!queryMessage) return;

    queryMessage.textContent = "";
    queryMessage.style.color = "";
}

function setQueryMessage(text, type = "") {
    const queryMessage = document.getElementById("queryMessage");
    if (!queryMessage) return;

    queryMessage.textContent = text || "";
    queryMessage.style.color =
        type === "error" ? "#f87171" :
        type === "success" ? "#31c48d" : "";
}

function scrollChatToBottom() {
    const chatThread = document.getElementById("chatThread");
    if (!chatThread) return;

    requestAnimationFrame(() => {
        chatThread.scrollTop = chatThread.scrollHeight;
    });
}

function createMessageRow(role, title, content) {
    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const card = document.createElement("div");
    card.className = "message-card";

    const meta = document.createElement("div");
    meta.className = "message-meta";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = role === "user" ? getUserInitial() : "AI";

    const titleEl = document.createElement("span");
    titleEl.textContent = `${title} • ${getCurrentTimeLabel()}`;

    meta.appendChild(avatar);
    meta.appendChild(titleEl);

    const body = document.createElement("div");
    body.className = "message-content";
    body.textContent = content;

    card.appendChild(meta);
    card.appendChild(body);
    row.appendChild(card);

    return { row, card, body };
}

function appendUserMessage(question) {
    hideWelcomePanel();

    const chatThread = document.getElementById("chatThread");
    if (!chatThread) return;

    const { row } = createMessageRow("user", "Vous", question);
    chatThread.appendChild(row);
    scrollChatToBottom();
}

function initUploadFilePreview() {
    const fileInput = document.getElementById("uploadFile");
    const fileName = document.getElementById("uploadFileName");
    const dropzone = document.getElementById("uploadDropzone");

    if (!fileInput || !fileName || !dropzone) return;

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
            dropzone.classList.add("has-file");
        } else {
            fileName.textContent = "Aucun fichier sélectionné";
            dropzone.classList.remove("has-file");
        }
    });
}

function appendAssistantThinking() {
    hideWelcomePanel();

    const chatThread = document.getElementById("chatThread");
    if (!chatThread) return null;

    const row = document.createElement("div");
    row.className = "message-row assistant";

    const card = document.createElement("div");
    card.className = "thinking-card";
    card.id = "thinkingCard";

    const label = document.createElement("span");
    label.textContent = "L’assistant analyse les documents";

    const dots = document.createElement("div");
    dots.className = "dots";
    dots.innerHTML = "<span></span><span></span><span></span>";

    card.appendChild(label);
    card.appendChild(dots);
    row.appendChild(card);
    chatThread.appendChild(row);

    scrollChatToBottom();
    return row;
}

async function typeText(element, text, speed = 8) {
    if (!element) return;
    element.textContent = "";

    for (let i = 0; i < text.length; i++) {
        element.textContent += text[i];
        if (i % 3 === 0) {
            await new Promise(resolve => setTimeout(resolve, speed));
        }
    }
}

function removeThinkingRow() {
    const thinkingCard = document.getElementById("thinkingCard");
    if (thinkingCard && thinkingCard.parentElement) {
        thinkingCard.parentElement.remove();
    }
}

function appendAssistantResponse(data) {
    const chatThread = document.getElementById("chatThread");
    if (!chatThread) return;

    const answer = data.answer || "Aucune réponse.";
    const sources = Array.isArray(data.sources) ? data.sources : [];
    const excerpts = Array.isArray(data.excerpts) ? data.excerpts : [];

    const { row, card, body } = createMessageRow("assistant", "Assistant IA", "");

    if (sources.length > 0) {
        const title = document.createElement("div");
        title.className = "message-block-title";
        title.textContent = "Sources";

        const wrap = document.createElement("div");
        wrap.className = "sources-wrap";

        sources.forEach(source => {
            const tag = document.createElement("span");
            tag.className = "source-tag";
            tag.textContent = source;
            wrap.appendChild(tag);
        });

        card.appendChild(title);
        card.appendChild(wrap);
    }

    if (excerpts.length > 0) {
        const title = document.createElement("div");
        title.className = "message-block-title";
        title.textContent = "Extraits";

        const list = document.createElement("div");
        list.className = "excerpts-list";

        excerpts.forEach(item => {
            const excerptCard = document.createElement("div");
            excerptCard.className = "excerpt-card";

            const top = document.createElement("div");
            top.className = "excerpt-top";
            top.innerHTML = `
                <span><strong>Document :</strong> ${item.document}</span>
                <span><strong>Chunk :</strong> ${item.chunk_index}</span>
                <span class="excerpt-score"><strong>Score :</strong> ${item.score}</span>
            `;

            const text = document.createElement("div");
            text.className = "message-content";
            text.textContent = item.text || "";

            excerptCard.appendChild(top);
            excerptCard.appendChild(text);
            list.appendChild(excerptCard);
        });

        card.appendChild(title);
        card.appendChild(list);
    }

    const aiBadge = document.createElement("div");
    aiBadge.className = "assistant-badge";
    aiBadge.textContent = "Réponse générée à partir des documents";

    card.appendChild(aiBadge);

    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-answer-btn";
    copyBtn.type = "button";
    copyBtn.textContent = "Copier la réponse";

    copyBtn.addEventListener("click", async () => {
        try {
            await navigator.clipboard.writeText(answer);
            showToast("Copie effectuée", "La réponse a été copiée dans le presse-papiers.", "success");
        } catch (error) {
            showToast("Copie impossible", "Le navigateur a refusé la copie.", "error");
        }
    });

    card.appendChild(copyBtn);

    chatThread.appendChild(row);
    scrollChatToBottom();
    typeText(body, answer, 6);

    scrollChatToBottom();
}

function initRefreshAllButton() {
    const refreshBtn = document.getElementById("refreshAllBtn");
    if (!refreshBtn) return;

    refreshBtn.addEventListener("click", async () => {
        refreshBtn.disabled = true;
        refreshBtn.textContent = "Actualisation...";

        try {
            await testHealth();
            await loadDocuments();
            await loadLogs();
            showToast("Dashboard actualisé", "Les informations administratives ont été mises à jour.", "success");
        } catch (error) {
            showToast("Actualisation impossible", "Une erreur est survenue.", "error");
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.textContent = "Actualiser tout";
        }
    });
}

function clearChat() {
    const chatThread = document.getElementById("chatThread");
    const questionInput = document.getElementById("questionInput");
    const welcomePanel = document.getElementById("welcomePanel");
    
    if (chatThread) {
        chatThread.innerHTML = "";
    }
    
    if (questionInput) {
        questionInput.value = "";
        autoResizeTextarea();
    }
    
    if (welcomePanel) {
        welcomePanel.classList.remove("hidden");
    }

    showToast("Nouvelle discussion", "La conversation a été réinitialisée.", "success");
    clearQueryMessage();
    focusComposer();
}

function focusComposer() {
    const input = document.getElementById("questionInput");
    if (!input) return;
    input.focus();
}

function fillQuestionAndSubmit(question) {
    const input = document.getElementById("questionInput");
    if (!input) return;

    input.value = question;
    autoResizeTextarea();

    const form = document.getElementById("queryForm");
    if (form) {
        form.requestSubmit();
    }
}

function initSuggestionButtons() {
    const suggestionButtons = document.querySelectorAll("[data-question]");
    suggestionButtons.forEach(button => {
        button.addEventListener("click", () => {
            const question = button.getAttribute("data-question") || "";
            fillQuestionAndSubmit(question);
        });
    });
}

function initClearChatButton() {
    const clearBtn = document.getElementById("clearChatBtn");
    if (!clearBtn) return;

    clearBtn.addEventListener("click", clearChat);
}

function initNewChatButton() {
    const newChatBtn = document.getElementById("newChatBtn");
    if (!newChatBtn) return;

    newChatBtn.addEventListener("click", clearChat);
}

function initComposerInput() {
    const input = document.getElementById("questionInput");
    if (!input) return;

    input.addEventListener("input", autoResizeTextarea);

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            const form = document.getElementById("queryForm");
            if (form) {
                form.requestSubmit();
            }
        }
    });

    autoResizeTextarea();
}

function initUploadForm() {
    const uploadForm = document.getElementById("uploadForm");
    if (!uploadForm) return;

    uploadForm.addEventListener("submit", handleUpload);
}

// async function handleQuery(event) {
//     event.preventDefault();

//     const questionInput = document.getElementById("questionInput");
//     const queryMessage = document.getElementById("queryMessage");
//     const queryResult = document.getElementById("queryResult");
//     const answerBox = document.getElementById("answerBox");
//     const sourcesList = document.getElementById("sourcesList");
//     const excerptsBox = document.getElementById("excerptsBox");

//     if (!questionInput || !queryMessage || !queryResult || !answerBox || !sourcesList || !excerptsBox) {
//         return;
//     }

//     const question = questionInput.value.trim();

//     queryMessage.textContent = "";
//     queryMessage.style.color = "";
//     answerBox.textContent = "";
//     sourcesList.innerHTML = "";
//     excerptsBox.innerHTML = "";
//     queryResult.style.display = "none";

//     if (!question) {
//         queryMessage.textContent = "Veuillez saisir une question.";
//         queryMessage.style.color = "red";
//         return;
//     }

//     try {
//         const response = await fetch("/query", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify({
//                 question: question
//             })
//         });

//         const data = await response.json().catch(() => ({}));

//         if (!response.ok) {
//             queryMessage.textContent = data.message || "Erreur lors de la requête.";
//             queryMessage.style.color = "red";
//             return;
//         }

//         queryResult.style.display = "block";
//         answerBox.textContent = data.answer || "Aucune réponse.";

//         if (Array.isArray(data.sources) && data.sources.length > 0) {
//             data.sources.forEach(source => {
//                 const li = document.createElement("li");
//                 li.textContent = source;
//                 sourcesList.appendChild(li);
//             });
//         } else {
//             const li = document.createElement("li");
//             li.textContent = "Aucune source.";
//             sourcesList.appendChild(li);
//         }

//         if (Array.isArray(data.excerpts) && data.excerpts.length > 0) {
//             data.excerpts.forEach(item => {
//                 const block = document.createElement("div");
//                 block.className = "excerpt-item";
//                 block.style.marginBottom = "15px";
//                 block.style.padding = "12px";
//                 block.style.border = "1px solid #e2e8f0";
//                 block.style.borderRadius = "8px";
//                 block.style.backgroundColor = "#f8fafc";

//                 block.innerHTML = `
//                     <strong>Document :</strong> ${item.document}<br>
//                     <strong>Chunk :</strong> ${item.chunk_index}<br>
//                     <strong>Score :</strong> ${item.score}<br>
//                     <strong>Extrait :</strong><br>
//                     ${item.text}
//                 `;

//                 excerptsBox.appendChild(block);
//             });
//         } else {
//             excerptsBox.textContent = "Aucun extrait disponible.";
//         }

//         queryMessage.textContent = "Requête traitée avec succès.";
//         queryMessage.style.color = "green";

//     } catch (error) {
//         queryMessage.textContent = "Erreur de communication avec le serveur.";
//         queryMessage.style.color = "red";
//     }
// }

async function handleQuery(event) {
    event.preventDefault();

    const questionInput = document.getElementById("questionInput");
    if (!questionInput) return;

    const question = questionInput.value.trim();

    clearQueryMessage();

    if (!question) {
        setQueryMessage("Veuillez saisir une question.", "error");
        return;
    }

    appendUserMessage(question);
    questionInput.value = "";
    autoResizeTextarea();

    const thinkingRow = appendAssistantThinking();

    try {
        const response = await fetch("/query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json().catch(() => ({}));

        removeThinkingRow();

        if (!response.ok) {
            setQueryMessage(data.message || "Erreur lors de la requête.", "error");
            appendAssistantResponse({
                answer: data.message || "Une erreur est survenue.",
                sources: [],
                excerpts: []
            });
            return;
        }

        appendAssistantResponse(data);
        setQueryMessage("Réponse générée avec succès.", "success");

    } catch (error) {
        removeThinkingRow();
        setQueryMessage("Erreur de communication avec le serveur.", "error");
        appendAssistantResponse({
            answer: "Je ne peux pas traiter la requête pour le moment.",
            sources: [],
            excerpts: []
        });
    }
}

function initQueryForm() {
    const queryForm = document.getElementById("queryForm");
    if (!queryForm) return;

    queryForm.addEventListener("submit", handleQuery);
}

function updateAdminStats({ healthText = null, documentsCount = null, logsCount = null } = {}) {
    const healthStat = document.getElementById("adminHealthStat");
    const documentsCountEl = document.getElementById("documentsCount");
    const logsCountEl = document.getElementById("logsCount");

    if (healthStat && healthText !== null) {
        healthStat.textContent = healthText;
    }

    if (documentsCountEl && documentsCount !== null) {
        documentsCountEl.textContent = String(documentsCount);
    }

    if (logsCountEl && logsCount !== null) {
        logsCountEl.textContent = String(logsCount);
    }
}

function initAdminNavButtons() {
    const buttons = document.querySelectorAll(".admin-nav-btn");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-target");
            const target = document.getElementById(targetId);

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
}

function initRefreshAllButton() {
    const refreshBtn = document.getElementById("refreshAllBtn");
    if (!refreshBtn) return;

    refreshBtn.addEventListener("click", async () => {
        await testHealth();
        await loadDocuments();
        await loadLogs();
    });
}

function refreshAdminAvatar() {
    const avatar = document.getElementById("userAvatar");
    if (!avatar) return;

    const sessionInfo = document.getElementById("sessionInfo");
    if (!sessionInfo || !sessionInfo.textContent) {
        avatar.textContent = "A";
        return;
    }

    const text = sessionInfo.textContent.trim();
    avatar.textContent = text.charAt(0).toUpperCase() || "A";
}


function showToast(title, text = "", type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <div class="toast-text">${text}</div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-6px)";
        toast.style.transition = "0.2s ease";
        setTimeout(() => toast.remove(), 220);
    }, 2600);
}


// document.addEventListener("DOMContentLoaded", () => {
//     testHealth();
//     initLoginForm();
//     loadSessionInfo();
//     initLogoutButton();
//     loadDocuments();
//     loadLogs();
//     initRefreshLogsButton();
//     initQueryForm();
//     initUploadForm();
// });



document.addEventListener("DOMContentLoaded", () => {
    testHealth();
    initLoginForm();
    loadSessionInfo();
    initLogoutButton();
    loadDocuments();
    loadLogs();
    initRefreshLogsButton();
    initQueryForm();
    initUploadForm();

    initSuggestionButtons();
    initClearChatButton();
    initNewChatButton();
    initComposerInput();

    initAdminNavButtons();
    initRefreshAllButton();
    initUploadFilePreview();
    focusComposer();
});