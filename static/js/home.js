const sell = (id) => {
    const buttons = document.querySelectorAll('button');
    buttons.forEach((button) => {
        button.disabled = true;
    })
    document.body.style.cursor='wait';
    data = {
        'id': id
    }
    $.post('/sell', data, (r) => {
        console.log(r);
        location.reload(true);
        notification("Transaction Successful.", 0);
    })
}
