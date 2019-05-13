function SendPause(){
	$("#PauseBtn").hide();
	$("#StartBtn").show();
	$.ajax({
		method:'POST',
		url:"/MIRRoutine",
		data:{
			'routine' : "PAUSE"
		},
		success:function(response){
			$("#feedback-danger div p").html(response);
			ShowDanger();
		}
	});
}

function SendReady(){
	$("#PauseBtn").show();
	$("#StartBtn").hide();
	$.ajax({
		method:'POST',
		url:"/MIRRoutine",
		data:{
			'routine' : "READY"
		},
		success:function(response){
			$("#feedback-success div p").html(response);
			ShowSuccess();
		}
	});
}

function ShowSuccess(){
	$("#feedback-success").fadeIn("slow");
	$("#feedback-danger").hide();
	$("#feedback-info").hide();
}

function ShowDanger(){
	$("#feedback-success").hide();
	$("#feedback-danger").fadeIn("slow");
	$("#feedback-info").hide();
}

function ShowInfo(){
	$("#feedback-success").hide();
	$("#feedback-danger").hide();
	$("#feedback-info").fadeIn("slow");
}

function CheckInit(){
	$.get("http://localhost:5000/CheckInit", function(data){
		if(data == "3"){
			console.log("MIR is in READY state");
			$("#PauseBtn").show();
			$("#StartBtn").hide();
		}
		else if(data == '4'){
			console.log("MIR is in PAUSE state");
			$("#PauseBtn").hide();
			$("#StartBtn").show();
		}
		else if(data == '5'){
			console.log("MIR is in EXECUTING state");
			$("#PauseBtn").show();
			$("#StartBtn").hide();
		}
	});
}

function PrintMissionName(){
	$.ajax({
		method:'GET',
		url:"/MissionList",
		success:function(response){
			var mission = response;
			var option = '';
			for (var i=0;i<mission.length;i++){
				option += '<option value="' + mission[i].guid + '">' + mission[i].name + '</option>';
			//Sample Output: '<option value="7f107423-e3a3-11e7-896e-f44d306f3f85">Go to Station 1</option>'
			}
			$("#SelectMission").html(option)
		}
	});
}

function SubmitMission() {
	var guid = $('#SelectMission').val();
	console.log(guid);
	$("#MissionCount").html("");
	SSErefreshInterval()
	$.ajax({
		method:'POST',
		url:"/SendMission",
		contentType: 'application/json',
		async: false,
		data: JSON.stringify({
              "mission_id": guid
            }),
		success:function(response){
			alert("Mission Queue Added!");
		}
	});
}

function DeleteMission(id){
	// var guid = document.getElementById("TEST").value;
  	
  	var r = confirm("Comfirm to delete mission?");
  	if (r == true){
  		console.log(id);
  		document.getElementById(id).remove();
  		$("#MissionCount").html("");
  		SSErefreshInterval()
  		$.ajax({
		method:'POST',
		url:"/DeleteMission",
		contentType: 'application/json',
		async: false,
		data: JSON.stringify({
              "mission_id": id
            }),
		success:function(response){
			alert("Mission Deleted!");
		}
	});
  	}
  	
}
function URPage(){

}

// Script for UR Controller
function OnGoingURMission(){
	$.ajax({
		method:'GET',
		url:"/URMissionHttp",
		success:function(response){
			if(response == "True"){
			console.log("UR mission in progress");
			$("#Step1Body").hide();
			$("#URMissionFBText").html("There is another UR mission on-going, <b>please refresh the page when it has completed.</b>");
			$("#mirfeedback div div span").removeClass("badge-success");
			$("#mirfeedback div div span").addClass("badge-danger");
			$("#mirfeedback div div span").html("Attention");
			$("#mirfeedback").fadeIn();
		}
		}
	});
}

function PickItem(item){
	$(item).toggleClass("opac");
	return 0;
}

function SubmitItem(){
	
	var ItemList = [];
	var i;
	for(i = 1; i < 6; i++){
		if($("#"+i).hasClass("opac")){
			ItemList.push($("#"+i).data("value"));
		}
	}
	if(ItemList.length == 0){
		alert("Please select at least one item!");
		var i;
		for(i=1; i<6 ;i++){
			$("#"+i).removeClass("opac");
			$("#Item"+i+"_container").show();	
		}
		return 0;
	}
	else{
		$("#Step1Body").fadeOut();
		$("#Step2Body").fadeIn();
		// console.log(ItemList);
		Step2BodyData(ItemList);
		return 0;
	}
	
}

function Step2BodyData(list){
	console.log(list);
	var i;
	var j=1;
	for(i = 0; i < list.length; i++){
		var name=list[i];
		$("#Item"+j+"_img").html('<img class="img-responsive" src="static/img/' + name +'.jpg" >');
		$("#Item"+j+"_name").html(name);
		$("#Item"+j+"_description").html('This is ' +name+', the product is blah blah blah');
		// console.log(i+1+"div written");
		j++;
	}
	HideEmptyDiv();
	return 0;
}

function HideEmptyDiv(){
	var k;
	for (k=1;k<6;k++){
		if($("#Item"+k+"_name").is(':empty')){
			$("#Item"+k+"_container").hide();
			// console.log(k+"div hide");
		}
	}
	return 0;
}

function Back1(){
	var i;
	for(i=1; i<6 ;i++){
		$("#"+i).removeClass("opac");
		$("#Item"+i+"_img").html("");
		$("#Item"+i+"_name").html("");
		$("#Item"+i+"_description").html("");
		$("#Item"+i+"_amount").val("");
		$("#Item"+i+"_container").show();	
	}
	$("#Step2Body").fadeOut();
	$("#Step1Body").fadeIn();
	return 0;
}

var ItemRequiredJSON = {
		required:{}
	};

function AddtoCart(){
	var i;
	var j;
	var RejectedDiv = [];
	var ItemName;
	var ItemAmount;
	var breaksig = false;
	ItemRequiredJSON = {
		required:{}
	};
	
	for(j=1;j<6;j++){
		if($("#Item"+j+"_container").css('display') == 'none'){
			var StopCounter = j;
			break;
		}
		if(j == 5){
			var StopCounter = 6;
		}
	}
	console.log(StopCounter);
	for (j=1;j<StopCounter;j++){
		var temp = $("#Item"+j+"_amount").val();
		if(!Number.isInteger(+temp) || (temp == "") || (temp == "0")){
			RejectedDiv.push(j);
			breaksig = true;		
		}	
	}
	if(breaksig == true){
		console.log(RejectedDiv);
		var k;
		for(k=0; k<RejectedDiv.length;k++){
			$("#Item"+RejectedDiv[k]+"_amount").addClass("is-invalid");
		}
		alert("Some input is invalid, please check");
		return -1;
	}
	else{
		var k;
		for(k=1; k<6;k++){
			$("#Item"+k+"_amount").removeClass("is-invalid");
		}
		for(i=1;i<StopCounter;i++){
			ItemName = $("#Item"+i+"_name").text();
			ItemAmount = $("#Item"+i+"_amount").val();
			ItemRequiredJSON.required[ItemName] = (+ItemAmount);
		}
		console.log(ItemRequiredJSON);
		Step3BodyData(ItemRequiredJSON);
		$("#Step2Body").fadeOut();
		$("#Step3Body").fadeIn();
	}
	
}
var HTMLData = "";

function Step3BodyData(JsonData){
	var NameList = Object.keys(JsonData.required);
	console.log(NameList);
	var i;
	HTMLData = "<center>";
	for(i=0;i<NameList.length;i++){
		// console.log('JsonData.'+NameList[i]);
		HTMLData += '<div class="Step3BodyImg"><img src="static/img/'+ NameList[i] +'.jpg"><h1><span class="badge badge-dark Step3BodyImgCaption">'+ JsonData.required[NameList[i]] +'</span></h1></div>'
	}
	HTMLData += "</center>"
	$("#ComfirmPackage").html(HTMLData);
	return 0;
}

function Back2(){
	$("#Step3Body").fadeOut();
	$("#Step2Body").fadeIn();
}
function ProgressBarSSE(){
	var source_info_progress = new EventSource("/ProgressBarSSE");
		
	source_info_progress.onmessage = function(event) {
	    var DataArr = event.data.split('_');
	    if(DataArr[0] == "TransmissionsEnded"){
	    	this.close();
	    	console.log("fuck");
	    }
	    else{
	    	console.log(DataArr);
		    $("#ProgressBarText").html(DataArr[0]);
		    $("#progressbar").css("width", DataArr[1]+"%")  
	    }
	    
	}
}
function SendURMission(){
	var r = confirm("Pickup mission will be sent to MIR, this can't be undone. Proceed?");
	if (r == true){
		ProgressBarSSE("on");
		$("#Step3Body").fadeOut();
		$.ajax({
			method:'POST',
			url:"/URMissionHttp",
			contentType: 'application/json',
			data: JSON.stringify(ItemRequiredJSON),
			success:function(response){
				$("#URMissionFBText").html(response);
				$("#RepickBtnDiv").removeClass("hidden");

			}
		});
		if(!$("#RepickBtnDiv").hasClass("hidden")){
			$("#RepickBtnDiv").addClass("hidden");
		}
		if ($("#mirfeedback div div span").hasClass("badge-danger")){
			$("#mirfeedback div div span").removeClass("badge-danger");
			$("#mirfeedback div div span").addClass("badge-success");
			$("#mirfeedback div div span").html("OK");
		}
		$("#URMissionFBText").html("Mission received, items are being collected, please be patient.");
		$("#ComfirmPackage2").html('<p class="card-text">Item being collected:</p>' + HTMLData);
		$("#mirfeedback").fadeIn();
		
	}
}

function Back3(){
	$("#RepickBtnDiv").addClass("hidden");
	$("#mirfeedback").fadeOut();
	for(var i=1; i<6 ;i++){
		$("#"+i).removeClass("opac");
		$("#Item"+i+"_img").html("");
		$("#Item"+i+"_name").html("");
		$("#Item"+i+"_description").html("");
		$("#Item"+i+"_amount").val("");
		$("#Item"+i+"_container").show();	
	}
	$("#Step1Body").fadeIn();
}