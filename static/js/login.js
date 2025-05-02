document.addEventListener("DOMContentLoaded", () => {
    gsap.from(".login-container", {
        opacity: 0,
        scale: 0.8,
        duration: 1,
        ease: "power3.out"
    });
});