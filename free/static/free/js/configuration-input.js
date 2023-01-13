class ConfigurationInput {
    constructor(config_node) {
      const configNode = config_node === null ? "configuration-input" : config_node;
      this.data = [];
  
      this.elementConfig = document.getElementById(configNode);
      this.findConfigInput();
      // this.updateElements();
    }
  
    findConfigInput() {
          const elementInputList = this.elementConfig.getElementsByTagName("input");
          // console.log(elementInputList);
      for (let elementInput of elementInputList) {
        let element = {
          "name": elementInput.id,
          "type": elementInput.type,
          "value": elementInput.value
        };
        // console.log(element);
        this.data.push(element);
      };
    }
    
    processElements() {
      const jsonData = {};
      
      this.data.forEach((element) => {
        if (element.type ==='number'){ 
          jsonData[element.name.replace("input_", "")] =Number(element.value) ;
        }
        else{
          jsonData[element.name.replace("input_", "")] = element.value;
        }
        
      });
  
      // console.log(jsonData);
      return jsonData;
    }
  
    updateElements() {
      setInterval(() => {
        console.log("UPDATE : ");
        this.findConfigInput();
        this.processElements();
      }, 5000);
    }
  
    getElements() {
      return this.data;
    }
  
  }
  
