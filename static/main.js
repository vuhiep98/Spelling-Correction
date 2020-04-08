function send_request(){
	var query = document.getElementById("input-query").value;
	var query_obj = {"query": query};
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() { 
		if (this.readyState == 4 && this.status == 200) {
			// response = JSON.parse(this.responseText);
			document.getElementById("correction-result").innerText = this.responseText;
			document.getElementById("suggestion").style.display = "block";
			// document.getElementsById("top1").innerText = result["top1"];
			// document.getElementsById("top2").innerText = result["top2"];
			// document.getElementsById("top3").innerText = result["top3"];	
		}
	};
	xhttp.open("POST", "/correct", true);
	xhttp.setRequestHeader("content-type", "application/json");
	xhttp.send(JSON.stringify(query_obj));
}		