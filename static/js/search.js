let canSearch = true;
const disableInput = () => {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((button) => {
        button.disabled = true;
    })
    document.body.style.cursor='wait';
    canSearch = false;
}

const enableInput = () => {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((button) => {
        button.disabled = false;
    })
    document.body.style.cursor='default';
    canSearch = true;
}
const sr = document.getElementById("search-result");


const search = () => {
    disableInput();
    setInterval(() => {
        const pCalc = document.getElementById("pCalc");
        let price = document.getElementById("price").innerText;
        let amount = document.getElementById("amount").value;
        pCalc.innerHTML = "Price for buy order: $ " + parseFloat(price) * parseInt(amount);
    },100)
    const ticker = document.getElementById("search-box").value;
    data = {
        'ticker': ticker
    }
    
    $.post("/query", data, (r) => {
        console.log("ran");
        const response = jQuery.parseJSON(r);
        sr.innerHTML = `
        <div class="display bg-secondary">
            <h1 class="text-primary tsize-2">${response['info']['longName']}</h1>
            <p class="text-primary">Price: $<z id="price">${response['info']['regularMarketPrice']}</z></p>
            <p class="text-primary">Day High/Low: $ ${response['info']['dayHigh']} / ${response['info']['dayLow']}</p>
            <br>
            <section>
                <input type="number" placeholder="Amount" id="amount" name="amount" value="1">
                <button class="button button-primary" onclick="buy('${ticker}');">BUY</button>
            </section>
            <p class="text-primary" id="pCalc">Price for buy order: </p>
        </div>
        `;
        enableInput();

    }).fail(() => {
        sr.innerHTML = "<p class='text-primary tsize-2'>No results...</p>";
        enableInput();
    })
}





document.onkeypress = function (e) {
    e = e || window.event;

    if(e.keyCode === 13) {
        if(canSearch) {
            search();
        }
    }
};


const buy = (ticker) => {
    let amount = document.getElementById("amount").value;
    data = {
        'ticker': ticker,
        'amount': amount
    }
    disableInput();
    let nb = document.getElementById("noti-box");
    $.post("/buy", data, (r) => {
        console.log("SUCCESS!");
        notification("Transaction Successful.", 0);
        enableInput();
        getWallet();
    }).fail(() => {
        console.log("FAIL!");
        notification("Transaction Failed.", 1);
        enableInput();
    })
}

