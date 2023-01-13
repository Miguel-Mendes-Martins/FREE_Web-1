let new_execution = JSON.parse(document.getElementById('execution-config').textContent);
console.log("test 28")
console.log(new_execution)
if ( Object.keys(new_execution).length  !== 0 && new_execution.status === "C")
{
  toggleDisable();
}
else{
  
}
var apparatusID = JSON.parse(document.getElementById('apparatus-id').textContent);
var protocolID = JSON.parse(document.getElementById('protocol-id').textContent);
var fullProtocol = JSON.parse(document.getElementById('protocol-config').textContent);

let save = 0;
let endpoint = "";
let method_queue = '';
let executionID = 0;
let Results=0;
var name = ''
var frist=0;
let table = "";
let last_result_id =0;
var QuizID = 0;


if (document.getElementById('apparatus-dt') != null){

  document.getElementById('apparatus-dt').innerHTML = String(apparatusID);
  document.getElementById('protocol-dt').innerHTML = String(protocolID);

  let html_tabele = document.getElementById("table_result").innerHTML; 
  let original_html_table = document.getElementById("table_result").innerHTML;
   
} 
else{
  QuizID = JSON.parse(document.getElementById('quiz-id').textContent);
  console.log(QuizID);
  console.log("quizid");
}

function enableContinueButton(){
  console.log(document.getElementById("continueButton").style.display)
  console.log("continuebutton")
  $("#continueButton").removeClass("disabled");
}

function toggleDisable(){
    //$("#startButton").toggleClass("disabled");
    $("#startButton").removeClass("disabled");

}

function changeButtons(){
  console.log("change buttons called")
  if (document.getElementById("createNew").style.display === "none") 
  {
    document.getElementById("createNew").style.display = null;
    document.getElementById("deleteButton").style.display = null;
    document.getElementById("saveNameButton").style.display = null;
    document.getElementById("saveButton").style.display = "none";
    document.getElementById("startButton").style.display = "none";
    document.getElementById("clearButton").style.display = "none";
  } 
  else {
    document.getElementById("createNew").style.display = "none";
    document.getElementById("deleteButton").style.display = "none";
    document.getElementById("saveNameButton").style.display = "none";
    document.getElementById("saveButton").style.display = null;
    document.getElementById("startButton").style.display = null;
    document.getElementById("clearButton").style.display = null;
  }
}


function disableButton(){
    //$("#startButton").toggleClass("disabled");
    $("#startButton").addClass("disabled");
}

function changeTabs(){
  document.getElementById("cena1").style.display = "none";
  document.getElementById("cena").style.display = null;
  document.getElementById("topTabResults").style.display = "none";
  document.getElementById("topTabExecution").style.display = null;
}

function enableInputs(){
  for (let paramet = 0; paramet < fullProtocol.required.length; paramet++){
    $("#range-"+String(fullProtocol.required[paramet])).removeClass("disabled");
    document.getElementById(String(fullProtocol.required[paramet])).disabled = false;
  }
}

function desableInputs(){
  for (let paramet = 0; paramet < fullProtocol.required.length; paramet++){
    $("#range-"+String(fullProtocol.required[paramet])).addClass("disabled");
    document.getElementById(String(fullProtocol.required[paramet])).disabled = true;
  }  
}

function restInputValeus(){
  for (let paramet = 0; paramet < fullProtocol.required.length; paramet++){
    document.getElementById(String(fullProtocol.required[paramet])).value = Number(fullProtocol.properties[String(fullProtocol.required[paramet])].default);
    $("#range-"+String(fullProtocol.required[paramet])).range('set value',  Number(fullProtocol.properties[String(fullProtocol.required[paramet])].default)); 
  }  
}



function goToCreateExecuiton(){
  //location.replace("http://"+window.location.hostname+":"+window.location.port+"/execution/create/"+String(apparatus)+"/"+String(protocol))
  window.history.pushState("","",'/execution/create/'+String(apparatusID)+"/"+String(protocolID))
  changeButtons()
  new_execution = {};
  disableButton();
  cleanPlots();
  enableInputs();
  changeTabs()
  restInputValeus();
  console.log(original_html_table);
  console.log(html_tabele);
  //table.destroy();
  $('#table_result_runtime').DataTable().rows().remove().draw();
  html_tabele = "";
  //document.getElementById("table_result").innerHTML = html_tabele;
  //updateTableRunTime();
  frist = 0;
}

function deleteExecution(){
  // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
  HEADERS = {
      "X-CSRFToken": document.getElementById('csrf_token').textContent,
      }
  // console.log("delete")
  // console.log(new_execution.id)
  var endpoint="/api/v1/execution/"+new_execution.id;

  axios({
      method: 'delete', //you can set what request you want to be
      url: endpoint,
      headers: HEADERS,
  }).then(response => {
      console.log('plotly_results', response);
      location.replace("http://"+window.location.hostname+":"+window.location.port+"/executions/finished")
  }).catch(console);
}




function save_name(){
    console.log("OUT : test");
    data_send = config
    data_send["name"] =  $("#name-of-exection").val();
    console.log(document.getElementById('csrf_token').textContent)
    // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
    HEADERS = {
        "X-CSRFToken": document.getElementById('csrf_token').textContent,
        }
    var endpoint="/api/v1/execution/"+new_execution.id+"/name";
    // print out
    console.log('JSON : ' +  endpoint);
    console.log(data_send);
    axios({
        method: 'patch', //you can set what request you want to be
        url: endpoint,
        headers: HEADERS,
        data: data_send,
    }).then(response => {
        console.log('plotly_results', response);
        toggleDisable();
    }).catch(console);
}


function queue(config) {
  console.log(QuizID)
  console.log(protocolID);
    if (Object.keys(new_execution).length  !== 0)
    {
      executionID = new_execution.id
      endpoint="/api/v1/execution/"+new_execution.id;
      method_queue = 'put'
      data_send = new_execution
    }
    else
    {
      endpoint="/api/v1/execution";
      method_queue = 'post';
      data_send = {"apparatus": apparatusID, "protocol": protocolID}
    }
    // get inputs values from the client side
    config_input.findConfigInput();
    data_send["config"] = config.processElements()
    data_send["quiz"] = QuizID;
  
    if ($("#name-of-exection").val() !== undefined){
      name = $("#name-of-exection").val();
      data_send["name"] = name 
    }
    else{
      data_send["name"] = ""
    }
   
  
    // '{"experiment_name": "Pendulo", "config_experiment": {"DeltaX":'+ String(DeltaX)+', "Samples":'+String(Samples)+' }}'
    HEADERS = {
      "X-CSRFToken": document.getElementById('csrf_token').textContent,
      }
    // print out
    console.log('JSON : ' +  endpoint);
    console.log('JSON1 : ' +  data_send["config"]);
    console.log(JSON.stringify(data_send));


  
    axios({
      method: method_queue, //you can set what request you want to be
      url: endpoint,
      headers: HEADERS,
      data: data_send,
    }).then(response => {
      if (method_queue === 'post')
      {
        //console.log("http://elab-dev.vps.tecnico.ulisboa.pt:8008/execution/"+String(response.data.id))
        //location.replace("http://elab-dev.vps.tecnico.ulisboa.pt:8008/execution/"+String(response.data.id))
        if(QuizID === 0){
          window.history.pushState("","",'/execution/'+String(response.data.id))
          //window.location.assign("","",'/execution/'+String(response.data.id)) //new line
        }
        else{
          window.location.reload();
        }
        new_execution = response.data;
      }
      console.log('plotly_results', response);
      toggleDisable();
    }).catch(console);  
  
  }
  
  
  const updateTableRunTime = () => {
    var currentDate = new Date()
    var seconds = currentDate.getSeconds();
      var minutes = currentDate.getMinutes();
      var hour = currentDate.getHours();
      var day = currentDate.getDate()
      var month = currentDate.getMonth() + 1  // starts from zero
      var year = currentDate.getFullYear()
  
     var d = day + "-" + month + "-" + year  + "  " + hour + "_" + minutes + "_" + seconds;
  
  
    // - MESSAGES
    $('.message .close').on('click', function() {
        $(this)
          .closest('.message')
          .transition('fade')
        ;
    });
    // - DATATABLES
    table = $('#table_result_runtime').DataTable({
          lengthChange: false,
          buttons: [ 'copy',
      {
                extend: 'csv',
                title: 'Pendulum_results__' + d  
            },
      {
                extend: 'excel',
                title: 'Pendulum_results__' +d
            },
      
      ]
      });
      table.buttons().container().appendTo(
        $('div.eight.column:eq(0)', table.table().container()) 
      );
  
  }
  
  $(document).ready(function(){
    updateTableRunTime(); 
 });



  const writeLineOnTable = (keys,response) => {
    table.destroy();
    html_tabele += `<tr>`;
    keys.forEach(function(data) 
    {
      
      html_tabele += `<td>` + response.data[0].value[data]  +  `</td>`;
      
      
    });
    html_tabele += `</tr>`;
    document.getElementById("table_result").innerHTML = html_tabele;
    updateTableRunTime();
  }
  
    function myStopFunction() {
        clearInterval(Results);
        console.log(Results);
        if(window.location !== window.parent.location){
          window.parent.postMessage("finished","*");
          console.log("POSTED FINISHED")
        }
    }

    function myStartFunction() {
        Results = setInterval(getData,500)
        console.log("Valor da função");
        console.log(Results);
    }

    // Receive data from experiment
    function getData(){
      let endpoint_result =  "/api/v1/execution/"+executionID+"/result/0";
      if (frist === 0)
      {
        endpoint_result = "/api/v1/execution/"+executionID+"/result/0";
      }
      else{
        endpoint_result = "/api/v1/execution/"+executionID+"/result/"+last_result_id
      }
    
      axios({
        method: 'get', //you can set what request you want to be
        url: endpoint_result,
        headers: HEADERS,
      }).then(response => {
        console.log('plotly_results', response.data);
        console.log('frist:', frist)
        if (frist === 0)
        {
          console.log("Responsedata:",response.data)
          if (response.data !== "")
          {
            frist = buildGraph(response)
            //frist = 1;
            // console.log(frist)
            last_result_id = response.data[0].id+1
          }
        }
        console.log("EE");
        console.log(response);
        // check for ending of the experiment
        if (response.data.result_type !== 'undefined' && response.data[0].result_type === 'f'){
            //$('#table_result_1').DataTable().ajax.reload();
            myStopFunction();
        }
        else{
          if (typeof response.data[0] === 'object'){
            console.log("here")
            plotRunTime(response)
            keys  = Object.keys(response.data[0].value);

            writeLineOnTable(keys,response)
    
            //  console.log("coisas html table ",html);
          }
          // getData();
        }
       
      }).catch(error => {
        if (error.response !== undefined) {
        console.error('Error : ', error.response.data);
        }
      });
      
    }

  
  function start() {
    executionID = new_execution.id;
    var endpoint_2="/api/v1/execution/"+executionID+"/start";
    console.log('JSON : ' +  endpoint_2);
    axios({
      method: 'put', //you can set what request you want to be
      url: endpoint_2,
      headers: HEADERS,
    }).then(response => {
      console.log('plotly_results', response);
    }).catch(error => {
      if (error.response !== undefined) {
      console.error('Error : ', error.response.data);
      }
    });
    
    $('.menu .item').tab('change tab','execution');
    myStartFunction();
    if(window.location === window.parent.location){
      changeButtons();}
    desableInputs();
  }
  
  function send_results(){

    console.log("Send Results");
    console.log(document.getElementById('csrf_token').textContent)
    var percent = document.getElementById('percent').textContent
    HEADERS = {
        "X-CSRFToken": document.getElementById('csrf_token').textContent,
        }
    var endpoint="/lti/grade/";
    axios({
        method: 'post', //you can set what request you want to be
        url: endpoint,
        headers: HEADERS,
        data: data_send,
    }).then(response => {
        console.log('plotly_results', response);
        toggleDisable();
    }).catch(console);

  }
