document.addEventListener("DOMContentLoaded", () => {
    // Animate form on load
    gsap.from(".parser", {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: "power3.out"
    });

    // Animate results if present
    if (document.querySelector(".results")) {
        gsap.from(".results", {
            opacity: 0,
            y: 30,
            duration: 0.8,
            delay: 0.5,
            ease: "power3.out"
        });
    }

    // Form submission feedback
    document.getElementById("parserForm").addEventListener("submit", () => {
        const btn = document.querySelector("button");
        btn.textContent = "Analyzing...";
        btn.disabled = true;
    });
});