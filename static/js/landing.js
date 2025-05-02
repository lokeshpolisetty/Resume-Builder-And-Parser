document.addEventListener("DOMContentLoaded", () => {
    // Animate cards on load
    gsap.from(".card", {
        opacity: 0,
        y: 50,
        duration: 1,
        stagger: 0.2,
        ease: "power3.out"
    });

    // Animate header
    gsap.from("header", {
        y: -100,
        duration: 0.8,
        ease: "power3.out"
    });

    // Hover effect
    document.querySelectorAll(".card").forEach(card => {
        card.addEventListener("mouseenter", () => {
            gsap.to(card, { scale: 1.02, duration: 0.3 });
        });
        card.addEventListener("mouseleave", () => {
            gsap.to(card, { scale: 1, duration: 0.3 });
        });
    });
});