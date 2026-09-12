const API = "/api/notes";

const form = document.getElementById("note-form");
const titleInput = document.getElementById("title");
const contentInput = document.getElementById("content");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const notesList = document.getElementById("notes-list");

let editingId = null;

async function fetchNotes() {
  const res = await fetch(API);
  const notes = await res.json();
  renderNotes(notes);
}

function renderNotes(notes) {
  notesList.innerHTML = "";

  if (notes.length === 0) {
    notesList.innerHTML = `<div class="empty-state">No notes yet. Add your first one above.</div>`;
    return;
  }

  for (const note of notes) {
    const card = document.createElement("div");
    card.className = "note-card";
    card.innerHTML = `
      <h3></h3>
      <p></p>
      <div class="note-meta"></div>
      <div class="note-actions">
        <button class="edit-btn">Edit</button>
        <button class="delete-btn">Delete</button>
      </div>
    `;
    card.querySelector("h3").textContent = note.title;
    card.querySelector("p").textContent = note.content;
    card.querySelector(".note-meta").textContent =
      "Updated " + new Date(note.updated_at).toLocaleString();

    card.querySelector(".edit-btn").addEventListener("click", () => startEdit(note));
    card.querySelector(".delete-btn").addEventListener("click", () => deleteNote(note.id));

    notesList.appendChild(card);
  }
}

function startEdit(note) {
  editingId = note.id;
  titleInput.value = note.title;
  contentInput.value = note.content;
  submitBtn.textContent = "Save Changes";
  cancelBtn.classList.remove("hidden");
  titleInput.focus();
}

function resetForm() {
  editingId = null;
  form.reset();
  submitBtn.textContent = "Add Note";
  cancelBtn.classList.add("hidden");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    title: titleInput.value.trim(),
    content: contentInput.value.trim(),
  };
  if (!payload.title) return;

  if (editingId) {
    await fetch(`${API}/${editingId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } else {
    await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }

  resetForm();
  fetchNotes();
});

cancelBtn.addEventListener("click", resetForm);

async function deleteNote(id) {
  if (!confirm("Delete this note?")) return;
  await fetch(`${API}/${id}`, { method: "DELETE" });
  fetchNotes();
}

fetchNotes();
