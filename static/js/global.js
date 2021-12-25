const notification = (s, type) => {
    let b = document.getElementById("nb");
    if(type == 0) {
        b.innerHTML += `
                <div class="notification n-success">
                    <p class="text-primary">${s}</p>
                </div>
            `;
    } else {
        b.innerHTML += `
                <div class="notification n-failure">
                    <p class="text-primary">${s}</p>
                </div>
            `;

    }
}