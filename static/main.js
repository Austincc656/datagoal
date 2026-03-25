// ===============================
// DEBUG: Confirm script is loaded
// ===============================
console.log("✅ Autocomplete script running...");

// ===============================
// Fetch team suggestions from backend
// ===============================
async function fetchTeamSuggestions(query) {
    try {
        const response = await fetch(`/team-search?q=${encodeURIComponent(query)}`);

        if (!response.ok) {
            console.error("❌ API error:", response.status);
            return [];
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("❌ Fetch failed:", error);
        return [];
    }
}

// ===============================
// Render dropdown suggestions
// ===============================
function renderSuggestions(box, teams, inputElement) {
    box.innerHTML = "";

    if (!teams || teams.length === 0) {
        box.style.display = "none";
        return;
    }

    teams.forEach((team) => {
        const item = document.createElement("div");
        item.className = "suggestion-item";

        const logo = team.logo
            ? `<img src="${team.logo}" alt="${team.name}" class="suggestion-logo">`
            : "";

        item.innerHTML = `
            ${logo}
            <div class="suggestion-text">
                <strong>${team.name}</strong>
                <small>${team.country || ""}</small>
            </div>
        `;

        // When user clicks suggestion
        item.addEventListener("click", () => {
            inputElement.value = team.name;
            box.innerHTML = "";
            box.style.display = "none";
        });

        box.appendChild(item);
    });

    box.style.display = "block";
}

// ===============================
// Setup autocomplete logic
// ===============================
function setupAutocomplete(inputId, boxId) {
    const inputElement = document.getElementById(inputId);
    const box = document.getElementById(boxId);

    if (!inputElement || !box) {
        console.warn(`⚠️ Missing elements: ${inputId} or ${boxId}`);
        return;
    }

    let debounceTimer;

    inputElement.addEventListener("input", () => {
        const query = inputElement.value.trim();

        console.log("⌨️ Typing:", query);

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            box.innerHTML = "";
            box.style.display = "none";
            return;
        }

        debounceTimer = setTimeout(async () => {
            console.log("🔍 Fetching suggestions for:", query);

            const teams = await fetchTeamSuggestions(query);

            console.log("📊 Results:", teams);

            renderSuggestions(box, teams, inputElement);
        }, 300); // slight delay for better UX
    });

    // Hide dropdown when clicking outside
    document.addEventListener("click", (event) => {
        if (!box.contains(event.target) && event.target !== inputElement) {
            box.style.display = "none";
        }
    });
}

// ===============================
// Initialize on page load
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Initializing autocomplete...");

    setupAutocomplete("home_team", "home_team_suggestions");
    setupAutocomplete("away_team", "away_team_suggestions");
});