
let tasks = [];

// Add task from form inputs
document.getElementById("addTask").addEventListener("click", () => {
  const title = document.getElementById("title").value;
  const due_date = document.getElementById("due_date").value;
  const importance = parseInt(document.getElementById("importance").value) || null;
  const estimated_hours = parseInt(document.getElementById("estimated_hours").value) || null;
  const dependencies = document.getElementById("dependencies").value
    ? document.getElementById("dependencies").value.split(",").map(d => d.trim())
    : [];

  if (!title) {
    alert("Task title is required");
    return;
  }

  const task = { title, due_date, importance, estimated_hours, dependencies };
  tasks.push(task);

  // Show current tasks in textarea as JSON
  document.getElementById("taskInput").value = JSON.stringify(tasks, null, 2);

  // Clear form
  document.getElementById("taskForm").reset();
});

// Analyze tasks
document.getElementById("analyze").addEventListener("click", () => {
  let payload;

  try {
    payload = JSON.parse(document.getElementById("taskInput").value);
  } catch (e) {
    alert("Invalid JSON format in bulk input");
    return;
  }

  const strategy = document.getElementById("strategy").value;

  fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ strategy, tasks: payload })
  })
    .then(response => response.json())
    .then(data => {
       if (!data.tasks || !Array.isArray(data.tasks)) {
         alert("Backend returned an error or invalid format");
         console.error("Invalid response:", data);
         return;
       }
       renderResults(data.tasks);
    })
    .catch(error => {
      console.error("Fetch error:", error);
      alert("Failed to connect to backend");
   });

   
});

// Render results as cards
function renderResults(tasks) {
  const container = document.getElementById("results");
  container.innerHTML = "";

  tasks.forEach(task => {
    const card = document.createElement("div");
    card.className = "card shadow-sm mb-3 p-3 border-start border-success border-3";
    card.innerHTML = `
      <h3>${task.title}</h3>
      <p><strong>Score:</strong> ${task.score}</p>
      <p><strong>Due Date:</strong> ${task.due_date || "N/A"}</p>
      <p><strong>Importance:</strong> ${task.importance || "N/A"}</p>
      <p><strong>Estimated Hours:</strong> ${task.estimated_hours || "N/A"}</p>
      <p><strong>Notes:</strong> ${(task.meta && task.meta.notes) ? task.meta.notes.join(", ") : "None"}</p>
    `;
    container.appendChild(card);
  });
}

//  Clear All Tasks button logic 
document.getElementById("clearBtn").addEventListener("click", () => {
  tasks = []; // reset tasks array
  document.getElementById("taskForm").reset();   // clears form inputs
  document.getElementById("taskInput").value = ""; // clears JSON textarea
  document.getElementById("results").innerHTML = ""; // clears results section
});