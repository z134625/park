function send_inp() {
    var user = document.getElementById("user").value;
    var con = document.getElementById("inp").value;
    var obj = {
        "msg": con,
    };
    var div = document.createElement("div");
    div.setAttribute("class", "b");
    var p = document.createElement("span");
    p.setAttribute("class", "spB");
    p.innerHTML = con;
    div.appendChild(p);
    var sp = document.createElement("span");
    sp.setAttribute("class", "nickB");
    sp.innerText = user;
    div.appendChild(sp);
    document.getElementById("chat").appendChild(div);
    document.getElementById("inp").value = "";

    $.ajax({
        url:"http://localhost:5003/ws",
        method : "POST",
        data : obj,
        success:function(result){
            var div = document.createElement("div");
            div.setAttribute("class", "a");
            var sp = document.createElement("span");
            sp.setAttribute("class", "nickA");
            sp.innerHTML = 'chatgpt';
            div.appendChild(sp);
            var p = document.createElement("span");
            p.setAttribute("class", "spA");
            p.innerHTML = result.msg;
            div.appendChild(p);
            document.getElementById("chat").appendChild(div)
    }});
}
