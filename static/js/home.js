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

const getLeague = () => {
    let title = document.getElementById("league-title");
    let cr = document.getElementById("item-container");

    $.post("/getTeam", (r) => {
        const response = jQuery.parseJSON(r);
        console.log(response);
        let placement = 1;
        cr.innerHTML = "";
        response.forEach((e) => {
            cr.innerHTML += `
            <div class="item" style="text-align: left; justify-content: space-between !important; width: 100%;">
                <p class="text-primary">${placement}.   ${e['username']}</p>
                <p class="text-primary">Score: ${e['score']}</p>
            </div>
            `;
            placement++;
        })
        cr.innerHTML += `
        <div class="item" style="text-align: left; justify-content: space-between !important; width: 100%;">
            <button class="button button-danger text-primary" onclick="leaveLeague();">Leave League</button>
        </div>
        `;
    }).fail(() => {
        cr.innerHTML = "";
        cr.innerHTML += `
            <div class="item" style="text-align: left; justify-content: space-between !important; width: 100%;">
                <p class="text-primary">Looks like you're not in a league.</p>
            </div>
            <div class="item" style="text-align: left; justify-content: space-between !important; width: 100%;">
                <button class="button button-primary text-primary" onclick="openPromt(1);">CREATE LEAGUE</button>
                <button class="button button-danger text-primary" onclick="openPromt(0);">JOIN LEAGUE</button> 
            </div>
            `;
    })
}

const openPromt = (state) => {
    let ipc = document.getElementById("ipc");
    $('#ipc').css('display', 'flex');
    if(state == 0) {
        
        ipc.innerHTML = `
        <h2 class="text-primary tsize-2">Join League</h2>
        <br>
        <input type="text" class="tsize-1-5" id="joinCode" placeholder="Enter league code">
        <br>
        <section>
            <button class="button button-primary text-primary" onclick="joinLeague();">Join</button>
            <button class="button button-danger text-primary" onclick="closePromt();">Cancel</button>
        </section>
        `;
    } else {
        ipc.innerHTML = `
        <h2 class="text-primary tsize-2">Create League</h2>
        <br>
        <input type="text" class="tsize-1-5" id="leagueName" placeholder="Enter league name">
        <br>
        <section>
            <button class="button button-primary text-primary" onclick="createLeague();">Create</button>
            <button class="button button-danger text-primary" onclick="closePromt();">Cancel</button>
        </section>
        `;
    }
}

const closePromt = () => {
    $('#ipc').css('display', 'none');
}

const joinLeague = () => {
    let joinCode = document.getElementById("joinCode").value;
    data = {
        'joinCode': joinCode
    }
    $.post("/joinLeague", data, (r) => {
        closePromt();
        location.reload(true);
    }).fail((r) => {
        console.log(r);
    })
}

const createLeague = () => {
    let leagueName = document.getElementById("leagueName").value;
    data = {
        'name': leagueName
    }
    $.post("/createLeague", data, (r) => {
        closePromt();
        location.reload(true);
    }).fail((r) => {
        console.log(r);
    })
}

const leaveLeague = () => {
    $.post("/leaveLeague", (r) => {
        location.reload(true);
    }).fail(() => {
        console.log("Leaving failed.");
    })
}

const getLeagueCode = () => {
    $.post("/getLeagueCode", (r) => {
        const response = jQuery.parseJSON(r);
        document.getElementById("jc").innerText = response['code'];
        document.getElementById("league-title").innerText = response['name'];
    
    }).failed(() => {
        console.log("getLeagueCode Error");
    })
}

getLeague();
getLeagueCode();