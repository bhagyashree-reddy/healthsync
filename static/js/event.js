function toggleContent(button) {
    const content = button.nextElementSibling;
    const readMoreButton = button;

    if (content.style.display === "none" || content.style.display === "") {
        content.style.display = "block";
        readMoreButton.style.position = "absolute";
        readMoreButton.style.right = "15px";
        // readMoreButton.style.marginTop="100px";
        readMoreButton.style.bottom = "15px";
        readMoreButton.textContent = "Read Less";
    } else {
        content.style.display = "none";
        readMoreButton.style.position = "static";
        readMoreButton.textContent = "Read More";
    }
}
