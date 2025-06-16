document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("resumeForm");
  const previewDiv = document.getElementById("preview");
  const previewContent = document.getElementById("previewContent");
  const previewPlaceholder = document.getElementById("previewPlaceholder");
  const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));

  // Function to show/hide preview
  function togglePreview(show) {
    if (show) {
      previewDiv.style.display = "block";
      previewPlaceholder.style.display = "none";
    } else {
      previewDiv.style.display = "none";
      previewPlaceholder.style.display = "flex";
    }
  }

  // UPDATED updatePreview to construct and send JSON data
  async function updatePreview() {
    try {
      // Build preview data explicitly
      const formData = new FormData(form);
      const data = {
        personal_info: {
          name: formData.get("name") || "",
          email: formData.get("email") || "",
          phone: formData.get("phone") || "",
          github: formData.get("github") || "",
          linkedin: formData.get("linkedin") || "",
        },
        summary: formData.get("summary") || "",
        experience: [],
        education: [],
        projects: [],
        skills: {
          "Technical Skills": formData.getAll("skills_group1[]").filter(skill => skill.trim()),
          "Soft Skills": formData.getAll("skills_group2[]").filter(skill => skill.trim()),
        },
      };

      // Collect experience data
      document.querySelectorAll("#experience .entry").forEach((entry) => {
        const title = entry.querySelector("[name='title']")?.value || "";
        const company = entry.querySelector("[name='company']")?.value || "";
        const duration = entry.querySelector("[name='duration']")?.value || "";
        const description = entry.querySelector("[name='description']")?.value || "";
        
        if (title || company) {
          data.experience.push({
            title,
            company,
            duration,
            description,
            responsibilities: Array.from(
              entry.querySelectorAll("[name='responsibility']")
            ).map((i) => i.value).filter(resp => resp.trim()),
          });
        }
      });

      // Collect education data
      document.querySelectorAll("#education .entry").forEach((entry) => {
        const degree = entry.querySelector("[name='degree']")?.value || "";
        const institution = entry.querySelector("[name='institution']")?.value || "";
        const year = entry.querySelector("[name='year']")?.value || "";
        const gpa = entry.querySelector("[name='gpa']")?.value || "";
        
        if (degree || institution) {
          data.education.push({
            degree,
            institution,
            year,
            gpa,
          });
        }
      });

      // Collect projects data
      document.querySelectorAll("#projects .entry").forEach((entry) => {
        const name = entry.querySelector("[name='name']")?.value || "";
        const description = entry.querySelector("[name='description']")?.value || "";
        const link = entry.querySelector("[name='link']")?.value || "";
        
        if (name || description) {
          data.projects.push({
            name,
            description,
            link,
          });
        }
      });

      const payload = new FormData();
      payload.append("data", JSON.stringify(data));

      // Call the HTML preview endpoint
      const res = await fetch("/preview_html", { method: "POST", body: payload });
      const result = await res.json();

      if (result.preview) {
        previewContent.innerHTML = result.preview;
        togglePreview(true);
      } else if (result.error) {
        console.error("Preview error:", result.error);
        togglePreview(false);
      }
    } catch (error) {
      console.error("Error updating preview:", error);
      togglePreview(false);
    }
  }

  // Throttle preview update during live typing
  let previewTimer;
  form.addEventListener("input", () => {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(updatePreview, 1000);
  });

  // Form submission handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const isPreview = e.submitter.name === "preview";
    
    if (isPreview) {
      updatePreview();
    } else {
      // Show loading modal
      loadingModal.show();
      
      try {
        // Build data for PDF generation
        const formData = new FormData(form);
        const data = {
          personal_info: {
            name: formData.get("name") || "",
            email: formData.get("email") || "",
            phone: formData.get("phone") || "",
            github: formData.get("github") || "",
            linkedin: formData.get("linkedin") || "",
          },
          summary: formData.get("summary") || "",
          experience: [],
          education: [],
          projects: [],
          skills: {
            "Technical Skills": formData.getAll("skills_group1[]").filter(skill => skill.trim()),
            "Soft Skills": formData.getAll("skills_group2[]").filter(skill => skill.trim()),
          },
        };

        // Collect all data (same as preview)
        document.querySelectorAll("#experience .entry").forEach((entry) => {
          const title = entry.querySelector("[name='title']")?.value || "";
          const company = entry.querySelector("[name='company']")?.value || "";
          const duration = entry.querySelector("[name='duration']")?.value || "";
          const description = entry.querySelector("[name='description']")?.value || "";
          
          if (title || company) {
            data.experience.push({
              title,
              company,
              duration,
              description,
              responsibilities: Array.from(
                entry.querySelectorAll("[name='responsibility']")
              ).map((i) => i.value).filter(resp => resp.trim()),
            });
          }
        });

        document.querySelectorAll("#education .entry").forEach((entry) => {
          const degree = entry.querySelector("[name='degree']")?.value || "";
          const institution = entry.querySelector("[name='institution']")?.value || "";
          const year = entry.querySelector("[name='year']")?.value || "";
          const gpa = entry.querySelector("[name='gpa']")?.value || "";
          
          if (degree || institution) {
            data.education.push({
              degree,
              institution,
              year,
              gpa,
            });
          }
        });

        document.querySelectorAll("#projects .entry").forEach((entry) => {
          const name = entry.querySelector("[name='name']")?.value || "";
          const description = entry.querySelector("[name='description']")?.value || "";
          const link = entry.querySelector("[name='link']")?.value || "";
          
          if (name || description) {
            data.projects.push({
              name,
              description,
              link,
            });
          }
        });

        const payload = new FormData();
        payload.append("data", JSON.stringify(data));
        payload.append("preview", "false");

        const res = await fetch("/builder", { method: "POST", body: payload });
        const result = await res.json();

        loadingModal.hide();

        if (result.download) {
          // Create download link
          const downloadUrl = `/download/pdf`;
          const a = document.createElement("a");
          a.href = downloadUrl;
          a.download = "resume.pdf";
          document.body.appendChild(a);
          a.click();
          a.remove();
          
          // Show success message
          const alert = document.createElement('div');
          alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
          alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
          alert.innerHTML = `
            <i class="bi bi-check-circle-fill me-2"></i>
            PDF generated successfully!
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          `;
          document.body.appendChild(alert);
          
          // Auto remove after 5 seconds
          setTimeout(() => {
            if (alert.parentNode) {
              alert.remove();
            }
          }, 5000);
        } else {
          throw new Error(result.error || "Unknown error occurred");
        }
      } catch (error) {
        loadingModal.hide();
        console.error("Error generating PDF:", error);
        
        // Show error message
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alert.innerHTML = `
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          Error generating PDF: ${error.message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
          if (alert.parentNode) {
            alert.remove();
          }
        }, 5000);
      }
    }
  });

  // Initial preview update if form has data
  setTimeout(() => {
    const hasData = form.querySelector('input[name="name"]').value.trim();
    if (hasData) {
      updatePreview();
    }
  }, 500);
});