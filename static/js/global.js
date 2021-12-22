const notification = (s, type) => {
    let b = document.querySelector('body');
    if(type == 0) {
        b.innerHTML += `
                <div class="notification n-success">
                    <p class="text-primary">Transaction Successful.</p>
                </div>
            `;
    } else {
        b.innerHTML += `
                <div class="notification n-failure">
                    <p class="text-primary">Transaction Failed.</p>
                </div>
            `;

    }
}