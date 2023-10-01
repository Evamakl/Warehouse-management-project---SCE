function checkApproved(){
    var check = document.getElementById("check");
    var btn = document.getElementById("btn");

    if(check.checked){
        btn.removeAttribute("disabled");
    }
    else{
        btn.disabled="true";
    }
}