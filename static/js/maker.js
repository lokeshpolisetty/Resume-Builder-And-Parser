document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("resumeForm");
  const previewDiv = document.getElementById("preview");
  const previewContent = document.getElementById("previewContent");

  // Function to clean LaTeX code into plain text
  function cleanLatex(latex) {
    return latex
      .replace(/\\begin\{[^\}]+\}/g, "")
      .replace(/\\end\{[^\}]+\}/g, "")
      .replace(/\\[a-zA-Z]+\{([^\}]+)\}/g, "$1")
      .replace(/\\[a-zA-Z]+\s?/g, "")
      .replace(/[\$\\]/g, "")
      .trim();
  }

  // UPDATED updatePreview to construct and send JSON data
  async function updatePreview() {
    // Build preview data explicitly
    const formData = new FormData(form);
    const data = {
      personal_info: {
        name: formData.get("name"),
        email: formData.get("email"),
        phone: formData.get("phone"),
        github: formData.get("github"),
        linkedin: formData.get("linkedin"),
      },
      summary: formData.get("summary"),
      experience: [],
      education: [],
      projects: [],
      skills: {
        "Some Skills": formData.getAll("skills_group1[]"),
        "Some More Skills": formData.getAll("skills_group2[]"),
      },
    };

    document.querySelectorAll("#experience .entry").forEach((entry) => {
      data.experience.push({
        title: entry.querySelector("[name='title']").value,
        company: entry.querySelector("[name='company']").value,
        duration: entry.querySelector("[name='duration']").value,
        description: entry.querySelector("[name='description']").value,
        responsibilities: Array.from(
          entry.querySelectorAll("[name='responsibility']")
        ).map((i) => i.value),
      });
    });
    document.querySelectorAll("#education .entry").forEach((entry) => {
      data.education.push({
        degree: entry.querySelector("[name='degree']").value,
        institution: entry.querySelector("[name='institution']").value,
        year: entry.querySelector("[name='year']").value,
        gpa: entry.querySelector("[name='gpa']").value,
      });
    });
    document.querySelectorAll("#projects .entry").forEach((entry) => {
      data.projects.push({
        name: entry.querySelector("[name='name']").value,
        description: entry.querySelector("[name='description']").value,
        link: entry.querySelector("[name='link']").value,
      });
    });

    const payload = new FormData();
    payload.append("data", JSON.stringify(data));
    payload.append("preview", "true");

    // Call the new HTML preview endpoint
    const res = await fetch("/preview_html", { method: "POST", body: payload });
    const result = await res.json();

    if (result.preview) {
      previewContent.innerHTML = result.preview;
      previewDiv.style.display = "block";
    }
  }

  // Throttle preview update during live typing (for example, every 800ms)
  let previewTimer;
  form.addEventListener("input", () => {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(updatePreview, 800);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isPreview = e.submitter.name === "preview";
    if (isPreview) {
      updatePreview();
    } else {
      // If download PDF, use fetch to download and trigger file save without leaving the page.
      const formData = new FormData(form);
      const data = {
        personal_info: {
          name: formData.get("name"),
          email: formData.get("email"),
          phone: formData.get("phone"),
          github: formData.get("github"),
          linkedin: formData.get("linkedin"),
        },
        summary: formData.get("summary"),
        experience: [],
        education: [],
        projects: [],
        skills: {
          "Some Skills": formData.getAll("skills_group1[]"),
          "Some More Skills": formData.getAll("skills_group2[]"),
        },
      };

      document.querySelectorAll("#experience .entry").forEach((entry) => {
        data.experience.push({
          title: entry.querySelector("[name='title']").value,
          company: entry.querySelector("[name='company']").value,
          duration: entry.querySelector("[name='duration']").value,
          description: entry.querySelector("[name='description']").value,
          responsibilities: Array.from(
            entry.querySelectorAll("[name='responsibility']")
          ).map((i) => i.value),
        });
      });
      document.querySelectorAll("#education .entry").forEach((entry) => {
        data.education.push({
          degree: entry.querySelector("[name='degree']").value,
          institution: entry.querySelector("[name='institution']").value,
          year: entry.querySelector("[name='year']").value,
          gpa: entry.querySelector("[name='gpa']").value,
        });
      });
      document.querySelectorAll("#projects .entry").forEach((entry) => {
        data.projects.push({
          name: entry.querySelector("[name='name']").value,
          description: entry.querySelector("[name='description']").value,
          link: entry.querySelector("[name='link']").value,
        });
      });

      const payload = new FormData();
      payload.append("data", JSON.stringify(data));
      payload.append("preview", "false");

      const res = await fetch("/builder", { method: "POST", body: payload });
      const result = await res.json();

      if (result.download) {
        // Fetch file as a blob and trigger download without leaving the page.
        const fileRes = await fetch("/download/" + result.download);
        const blob = await fileRes.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "resume.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        alert("PDF downloaded successfully!");
      } else {
        alert(result.error || "Unknown error");
      }
    }
  });
});

function addExperience() {
  const div = document.createElement("div");
  div.className = "entry";
  div.innerHTML = `
        <input name="title" placeholder="Title">
        <input name="company" placeholder="Company">
        <input name="duration" placeholder="Duration">
        <textarea name="description" placeholder="Description"></textarea>
        <input name="responsibility" placeholder="Responsibility">
        <input name="responsibility" placeholder="Responsibility">
    `;
  document.getElementById("experience").appendChild(div);
}

function addEducation() {
  const div = document.createElement("div");
  div.className = "entry";
  div.innerHTML = `
        <input name="degree" placeholder="Degree">
        <input name="institution" placeholder="Institution">
        <input name="year" placeholder="Year">
        <input name="gpa" placeholder="GPA (optional)">
    `;
  document.getElementById("education").appendChild(div);
}

function addProject() {
  const div = document.createElement("div");
  div.className = "entry";
  div.innerHTML = `
        <input name="name" placeholder="Project Name">
        <textarea name="description" placeholder="Project Description"></textarea>
        <input name="link" placeholder="Project Link (optional)">
    `;
  document.getElementById("projects").appendChild(div);
}

function addSkill(groupName) {
  const input = document.createElement("input");
  input.name = groupName + "[]";
  input.placeholder = groupName.includes("1")
    ? "Technical Skill"
    : "Soft Skill";
  document
    .querySelector(`[name='${groupName}[]']`)
    .parentNode.appendChild(input);
}
